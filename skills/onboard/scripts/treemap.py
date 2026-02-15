#!/usr/bin/env python3
"""
Tree-sitter codebase mapper and code smell detector.

Walks the current working directory, parses source files with tree-sitter,
and emits a structural map + prioritized code smell report.

Requires: pip install tree-sitter tree-sitter-python tree-sitter-javascript
           tree-sitter-typescript tree-sitter-rust tree-sitter-go
           tree-sitter-java tree-sitter-ruby
"""

import os
import subprocess
import sys
import warnings
from collections import defaultdict
from pathlib import Path

from tree_sitter import Language, Parser

# Suppress deprecation warnings from tree-sitter internals
warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")

# ---------------------------------------------------------------------------
# Language loading (tree-sitter 0.25+ with individual packages)
# ---------------------------------------------------------------------------

_LANGUAGES: dict[str, Language] = {}
_PARSERS: dict[str, Parser] = {}


def _load_languages():
    """Load all available tree-sitter languages."""
    loaders = {
        "python": ("tree_sitter_python", "language"),
        "javascript": ("tree_sitter_javascript", "language"),
        "typescript": ("tree_sitter_typescript", "language_typescript"),
        "tsx": ("tree_sitter_typescript", "language_tsx"),
        "rust": ("tree_sitter_rust", "language"),
        "go": ("tree_sitter_go", "language"),
        "java": ("tree_sitter_java", "language"),
        "ruby": ("tree_sitter_ruby", "language"),
    }
    for lang_name, (module_name, func_name) in loaders.items():
        try:
            mod = __import__(module_name)
            lang_func = getattr(mod, func_name)
            _LANGUAGES[lang_name] = Language(lang_func())
        except (ImportError, AttributeError, Exception):
            pass  # Language not installed, skip


def get_parser(lang: str) -> Parser | None:
    """Get a parser for the given language."""
    if lang not in _PARSERS:
        if lang not in _LANGUAGES:
            return None
        p = Parser(_LANGUAGES[lang])
        _PARSERS[lang] = p
    return _PARSERS[lang]


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", "venv", ".venv", "env",
    "dist", "build", ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".next", ".nuxt", "target", "out", ".eggs", "*.egg-info",
    ".claude", ".idea", ".vscode", "coverage", "htmlcov",
}

EXT_TO_LANG = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
}

# Smell thresholds
LONG_FUNC_LINES = 50
GOD_CLASS_METHODS = 15
DEEP_NESTING_LEVELS = 4
MANY_PARAMS = 5
LARGE_FILE_LINES = 500

# ---------------------------------------------------------------------------
# Tree-sitter queries per language
# ---------------------------------------------------------------------------

# Node types that represent classes, functions, imports for each language.
LANG_NODE_TYPES = {
    "python": {
        "classes": ["class_definition"],
        "functions": ["function_definition"],
        "imports": ["import_statement", "import_from_statement"],
        "decorators": ["decorator"],
        "docstrings": ["expression_statement"],
        "except_clauses": ["except_clause"],
    },
    "typescript": {
        "classes": ["class_declaration"],
        "functions": ["function_declaration", "method_definition", "arrow_function"],
        "imports": ["import_statement"],
        "interfaces": ["interface_declaration"],
        "type_aliases": ["type_alias_declaration"],
    },
    "tsx": {
        "classes": ["class_declaration"],
        "functions": ["function_declaration", "method_definition", "arrow_function"],
        "imports": ["import_statement"],
        "interfaces": ["interface_declaration"],
        "type_aliases": ["type_alias_declaration"],
    },
    "javascript": {
        "classes": ["class_declaration"],
        "functions": ["function_declaration", "method_definition", "arrow_function"],
        "imports": ["import_statement"],
    },
    "rust": {
        "classes": ["struct_item", "enum_item", "impl_item"],
        "functions": ["function_item"],
        "imports": ["use_declaration"],
    },
    "go": {
        "classes": ["type_declaration"],
        "functions": ["function_declaration", "method_declaration"],
        "imports": ["import_declaration"],
    },
    "java": {
        "classes": ["class_declaration", "interface_declaration", "enum_declaration"],
        "functions": ["method_declaration", "constructor_declaration"],
        "imports": ["import_declaration"],
    },
    "ruby": {
        "classes": ["class", "module"],
        "functions": ["method", "singleton_method"],
        "imports": ["call"],  # require/require_relative
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def should_ignore(path: Path) -> bool:
    """Check if any component of the path matches an ignore pattern."""
    parts = path.parts
    for part in parts:
        if part in IGNORE_DIRS:
            return True
        for pattern in IGNORE_DIRS:
            if "*" in pattern and part.endswith(pattern.replace("*", "")):
                return True
    return False


def get_node_name(node) -> str | None:
    """Extract the name from a tree-sitter node."""
    for child in node.children:
        if child.type in ("identifier", "name", "type_identifier", "property_identifier"):
            return child.text.decode("utf-8")
        if child.type == "dotted_name":
            return child.text.decode("utf-8")
    return None


def get_function_params(node, lang: str) -> list[str]:
    """Extract parameter names from a function node."""
    params = []
    for child in node.children:
        if child.type in ("parameters", "formal_parameters", "parameter_list"):
            for param in child.children:
                if param.type in (
                    "identifier", "typed_parameter", "typed_default_parameter",
                    "default_parameter", "required_parameter", "optional_parameter",
                    "formal_parameter", "parameter",
                ):
                    name = get_node_name(param)
                    if name and name not in ("self", "cls"):
                        params.append(name)
                    elif param.type == "identifier" and param.text:
                        text = param.text.decode("utf-8")
                        if text not in ("self", "cls"):
                            params.append(text)
    return params


def count_nesting_depth(node, current_depth: int = 0) -> int:
    """Find the maximum nesting depth of control flow in a node."""
    nesting_types = {
        "if_statement", "for_statement", "while_statement", "try_statement",
        "with_statement", "for_in_statement", "if_expression",
        "match_statement", "case_clause",
        "switch_statement", "for_of_statement",
    }
    max_depth = current_depth
    for child in node.children:
        if child.type in nesting_types:
            child_depth = count_nesting_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        else:
            child_depth = count_nesting_depth(child, current_depth)
            max_depth = max(max_depth, child_depth)
    return max_depth


def has_docstring(node) -> bool:
    """Check if a Python function or class has a docstring as its first statement."""
    body = None
    for child in node.children:
        if child.type == "block":
            body = child
            break
    if body is None:
        return True  # Can't tell, assume fine
    for child in body.children:
        if child.type == "expression_statement":
            for sub in child.children:
                if sub.type == "string":
                    return True
            return False
        elif child.type == "comment":
            continue
        else:
            return False
    return False


def is_catchall_except(node) -> bool:
    """Check if an except clause is a bare except or catches Exception."""
    children_types = [c.type for c in node.children]
    if "except" in children_types or node.type == "except_clause":
        has_type = False
        for child in node.children:
            if child.type in ("identifier", "as_pattern"):
                text = child.text.decode("utf-8") if child.text else ""
                if "Exception" in text:
                    return True
                has_type = True
        # bare except: with no type specified
        if not has_type and node.child_count <= 3:
            texts = [c.text.decode("utf-8") for c in node.children if c.text]
            if "except" in texts and not any(
                c.type in ("identifier", "as_pattern", "tuple") for c in node.children
            ):
                return True
    return False


def get_import_text(node) -> str:
    """Get a readable import string from an import node."""
    text = node.text.decode("utf-8").strip()
    if len(text) > 80:
        text = text[:77] + "..."
    return text


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------


class CodebaseMapper:
    def __init__(self, root: Path):
        self.root = root
        self.files_parsed = 0
        self.file_data: dict[str, dict] = {}  # rel_path -> parsed info
        self.smells: list[dict] = []
        self.import_graph: dict[str, set[str]] = defaultdict(set)  # module -> imports

    def scan(self):
        """Walk the codebase and parse all recognized source files."""
        for dirpath, dirnames, filenames in os.walk(self.root):
            rel_dir = Path(dirpath).relative_to(self.root)
            if should_ignore(rel_dir):
                dirnames.clear()
                continue
            # Prune ignored dirs from traversal
            dirnames[:] = [
                d for d in dirnames
                if not should_ignore(rel_dir / d)
            ]
            for fname in sorted(filenames):
                fpath = Path(dirpath) / fname
                ext = fpath.suffix
                if ext not in EXT_TO_LANG:
                    continue
                lang = EXT_TO_LANG[ext]
                rel_path = str(fpath.relative_to(self.root))
                self._parse_file(fpath, rel_path, lang)

    def _parse_file(self, fpath: Path, rel_path: str, lang: str):
        """Parse a single file with tree-sitter."""
        try:
            source = fpath.read_bytes()
        except (OSError, PermissionError):
            return

        parser = get_parser(lang)
        if parser is None:
            return

        try:
            tree = parser.parse(source)
        except Exception:
            return

        self.files_parsed += 1
        source_text = source.decode("utf-8", errors="replace")
        line_count = source_text.count("\n") + 1

        # Check large file smell
        if line_count > LARGE_FILE_LINES:
            self.smells.append({
                "type": "LARGE_FILE",
                "severity": "low",
                "file": rel_path,
                "line": None,
                "detail": f"{line_count:,} lines",
            })

        node_types = LANG_NODE_TYPES.get(lang, {})
        classes = []
        functions = []
        imports = []
        interfaces = []
        type_aliases = []

        self._walk_tree(
            tree.root_node, rel_path, lang, node_types,
            classes, functions, imports, interfaces, type_aliases,
            source_text,
        )

        # Build import graph (Python-specific)
        if lang == "python":
            module_name = rel_path.replace("/", ".").replace(".py", "")
            for imp_text in imports:
                parts = imp_text.split()
                if len(parts) >= 2 and parts[0] == "from":
                    imported_module = parts[1]
                elif len(parts) >= 2 and parts[0] == "import":
                    imported_module = parts[1].rstrip(",")
                else:
                    continue
                self.import_graph[module_name].add(imported_module)

        self.file_data[rel_path] = {
            "lang": lang,
            "classes": classes,
            "functions": functions,
            "imports": imports,
            "interfaces": interfaces,
            "type_aliases": type_aliases,
            "line_count": line_count,
        }

    def _walk_tree(
        self, node, rel_path, lang, node_types,
        classes, functions, imports, interfaces, type_aliases,
        source_text,
    ):
        """Recursively walk the AST and extract structural info + smells."""
        # Classes
        if node.type in node_types.get("classes", []):
            name = get_node_name(node)
            if name:
                classes.append(name)
                # Count methods for god class detection
                method_count = 0
                for child in node.children:
                    if child.type in ("block", "class_body", "declaration_list"):
                        for member in child.children:
                            if member.type in (
                                "function_definition", "method_definition",
                                "method_declaration", "function_item",
                            ):
                                method_count += 1
                if method_count > GOD_CLASS_METHODS:
                    self.smells.append({
                        "type": "GOD_CLASS",
                        "severity": "high",
                        "file": rel_path,
                        "line": node.start_point[0] + 1,
                        "detail": f"{name} has {method_count} methods",
                    })
                # Missing docstring (Python) — skip test files
                if lang == "python" and not has_docstring(node) and not rel_path.startswith("tests/"):
                    self.smells.append({
                        "type": "MISSING_DOCSTRING",
                        "severity": "low",
                        "file": rel_path,
                        "line": node.start_point[0] + 1,
                        "detail": f"class {name}",
                    })

        # Functions
        if node.type in node_types.get("functions", []):
            name = get_node_name(node)
            if name:
                functions.append(name)

                # Long function detection
                func_lines = node.end_point[0] - node.start_point[0] + 1
                if func_lines > LONG_FUNC_LINES:
                    self.smells.append({
                        "type": "LONG_FUNCTION",
                        "severity": "medium",
                        "file": rel_path,
                        "line": node.start_point[0] + 1,
                        "detail": f"{name}() is {func_lines} lines",
                    })

                # Deep nesting detection
                depth = count_nesting_depth(node)
                if depth > DEEP_NESTING_LEVELS:
                    self.smells.append({
                        "type": "DEEP_NESTING",
                        "severity": "medium",
                        "file": rel_path,
                        "line": node.start_point[0] + 1,
                        "detail": f"{name}() has {depth} nesting levels",
                    })

                # Too many parameters
                params = get_function_params(node, lang)
                if len(params) > MANY_PARAMS:
                    self.smells.append({
                        "type": "MANY_PARAMS",
                        "severity": "medium",
                        "file": rel_path,
                        "line": node.start_point[0] + 1,
                        "detail": f"{name}() has {len(params)} parameters",
                    })

                # Missing docstring (Python) — skip test files and test_ functions
                if (lang == "python" and not has_docstring(node)
                        and not name.startswith("_")
                        and not name.startswith("test_")
                        and not rel_path.startswith("tests/")):
                    self.smells.append({
                        "type": "MISSING_DOCSTRING",
                        "severity": "low",
                        "file": rel_path,
                        "line": node.start_point[0] + 1,
                        "detail": f"{name}()",
                    })

        # Imports
        if node.type in node_types.get("imports", []):
            imp_text = get_import_text(node)
            if imp_text:
                imports.append(imp_text)

        # Interfaces (TS/TSX)
        if node.type in node_types.get("interfaces", []):
            name = get_node_name(node)
            if name:
                interfaces.append(name)

        # Type aliases (TS/TSX)
        if node.type in node_types.get("type_aliases", []):
            name = get_node_name(node)
            if name:
                type_aliases.append(name)

        # Catch-all exceptions (Python)
        if lang == "python" and node.type == "except_clause":
            if is_catchall_except(node):
                self.smells.append({
                    "type": "CATCH_ALL_EXCEPTION",
                    "severity": "high",
                    "file": rel_path,
                    "line": node.start_point[0] + 1,
                    "detail": node.text.decode("utf-8", errors="replace").split("\n")[0].strip(),
                })

        # Recurse into children
        for child in node.children:
            self._walk_tree(
                child, rel_path, lang, node_types,
                classes, functions, imports, interfaces, type_aliases,
                source_text,
            )

    def detect_circular_imports(self):
        """Detect circular import cycles in the import graph."""
        known_modules = set(self.import_graph.keys())

        def find_cycles():
            visited = set()
            rec_stack = set()
            cycles = []

            def dfs(module, path):
                visited.add(module)
                rec_stack.add(module)
                path.append(module)

                for imported in self.import_graph.get(module, set()):
                    matched = None
                    for known in known_modules:
                        if known == imported or known.endswith("." + imported):
                            matched = known
                            break
                        if imported.startswith("."):
                            base = ".".join(module.split(".")[:-1])
                            candidate = base + imported
                            if candidate in known_modules:
                                matched = candidate
                                break

                    if matched:
                        if matched in rec_stack:
                            cycle_start = path.index(matched)
                            cycle = path[cycle_start:] + [matched]
                            cycles.append(cycle)
                        elif matched not in visited:
                            dfs(matched, path)

                path.pop()
                rec_stack.discard(module)

            for module in known_modules:
                if module not in visited:
                    dfs(module, [])

            return cycles

        cycles = find_cycles()
        seen = set()
        for cycle in cycles:
            key = " -> ".join(sorted(cycle[:-1]))
            if key not in seen:
                seen.add(key)
                self.smells.append({
                    "type": "CIRCULAR_IMPORT",
                    "severity": "high",
                    "file": cycle[0].replace(".", "/") + ".py",
                    "line": None,
                    "detail": " -> ".join(cycle),
                })

    def format_output(self) -> str:
        """Format the structural map and smell report."""
        lines = []
        lines.append(f"# Codebase Structure ({self.files_parsed} files parsed)\n")

        # Group files by top-level directory
        by_dir: dict[str, list[str]] = defaultdict(list)
        for rel_path in sorted(self.file_data.keys()):
            parts = rel_path.split("/")
            top_dir = parts[0] if len(parts) > 1 else "."
            by_dir[top_dir].append(rel_path)

        for dir_name in sorted(by_dir.keys()):
            lines.append(f"## {dir_name}/\n")
            for rel_path in by_dir[dir_name]:
                info = self.file_data[rel_path]
                lines.append(f"**{rel_path}** ({info['lang']}, {info['line_count']} lines)")

                if info["classes"]:
                    lines.append(f"  - classes: {', '.join(info['classes'])}")
                if info["interfaces"]:
                    lines.append(f"  - interfaces: {', '.join(info['interfaces'])}")
                if info["type_aliases"]:
                    lines.append(f"  - types: {', '.join(info['type_aliases'])}")
                if info["functions"]:
                    funcs = info["functions"]
                    if len(funcs) > 20:
                        display = ", ".join(funcs[:20]) + f" ... (+{len(funcs) - 20} more)"
                    else:
                        display = ", ".join(funcs)
                    lines.append(f"  - functions: {display}")
                if info["imports"]:
                    imp_names = []
                    for imp in info["imports"]:
                        parts = imp.split()
                        if len(parts) >= 2:
                            mod = parts[1] if parts[0] in ("import", "from") else parts[0]
                            imp_names.append(mod.rstrip(","))
                    unique_imports = list(dict.fromkeys(imp_names))
                    if len(unique_imports) > 15:
                        display = ", ".join(unique_imports[:15]) + f" ... (+{len(unique_imports) - 15} more)"
                    else:
                        display = ", ".join(unique_imports)
                    lines.append(f"  - imports: {display}")
                lines.append("")

        # Smell report
        if self.smells:
            lines.append(f"\n# Code Smells ({len(self.smells)} issues found)\n")

            severity_labels = {"high": "High Priority", "medium": "Medium Priority", "low": "Low Priority"}

            by_severity = defaultdict(list)
            for smell in self.smells:
                by_severity[smell["severity"]].append(smell)

            MAX_PER_TYPE = 15  # Cap output per smell type to avoid noise

            for sev in ("high", "medium", "low"):
                items = by_severity.get(sev, [])
                if not items:
                    continue
                lines.append(f"## {severity_labels[sev]}\n")

                # Group by type within severity, cap each type
                by_type: dict[str, list[dict]] = defaultdict(list)
                for s in sorted(items, key=lambda x: (x["file"], x.get("line") or 0)):
                    by_type[s["type"]].append(s)

                for smell_type, type_items in by_type.items():
                    shown = type_items[:MAX_PER_TYPE]
                    for s in shown:
                        loc = s["file"]
                        if s.get("line"):
                            loc += f":{s['line']}"
                        lines.append(f"- [{s['type']}] {loc} — {s['detail']}")
                    if len(type_items) > MAX_PER_TYPE:
                        lines.append(f"  ... and {len(type_items) - MAX_PER_TYPE} more {smell_type} issues")
                lines.append("")
        else:
            lines.append("\n# Code Smells (0 issues found)\n")
            lines.append("No code smells detected. Nice!\n")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def get_git_head() -> str | None:
    """Get the current HEAD commit hash and subject."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H %s", "-1"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def main():
    _load_languages()
    root = Path.cwd()

    # Print HEAD commit info
    head = get_git_head()
    if head:
        print(f"# Git HEAD at onboarding: {head}\n")

    mapper = CodebaseMapper(root)
    mapper.scan()
    mapper.detect_circular_imports()
    print(mapper.format_output())


if __name__ == "__main__":
    main()
