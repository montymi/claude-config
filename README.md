<!-- Shields bar -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- Project header -->
<div align="center">
  <h1>claude-config</h1>
  <p>Personal Claude Code skills and configuration, version-controlled and portable across machines.</p>
  <a href="https://github.com/montymi/claude-config"><strong>Explore the docs</strong></a>
  &middot;
  <a href="https://github.com/montymi/claude-config/issues/new?labels=bug">Report Bug</a>
  &middot;
  <a href="https://github.com/montymi/claude-config/issues/new?labels=enhancement">Request Feature</a>
</div>

<!-- Table of Contents -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#built-with">Built With</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#structure">Structure</a></li>
    <li><a href="#tasks">Tasks</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

---

## About The Project

claude-config is a version-controlled collection of custom [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills and configuration. It provides portable, reusable slash commands that extend Claude Code with project-specific workflows — from codebase onboarding and README generation to conventional commits, code review, test scaffolding, and document analysis.

The goal is to keep Claude Code customizations in a single repository that can be cloned onto any machine, symlinked into `~/.claude/skills/`, and immediately available in every Claude Code session. Skills are self-contained directories with a `SKILL.md` definition file and optional supporting scripts — adding a new one is as simple as dropping a directory and re-running the installer.

Three skills are **script-backed** and use [tree-sitter](https://tree-sitter.github.io/tree-sitter/) for structural analysis:
- `/onboard` parses source code across 11 languages to extract architecture maps and detect code smells
- `/aap` parses Agent Action Plan documents for structural review and LoC estimation
- `/tech-spec` parses Technical Specification documents for completeness and consistency review

The remaining seven skills — `/readme`, `/commit`, `/lint`, `/test`, `/dev-doc`, `/z` — are **prompt-only**, relying on Claude Code's built-in tools for their workflows.

## Built With

[![Python][python-shield]][python-url]
[![Bash][bash-shield]][bash-url]

## Getting Started

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed (`~/.claude/` must exist)
- Python 3.10+
- git

### Installation

```bash
git clone https://github.com/montymi/claude-config.git ~/Projects/claude-config
cd ~/Projects/claude-config
chmod +x install.sh
./install.sh
```

The installer will:
1. Symlink each skill directory into `~/.claude/skills/`
2. Install Python dependencies (tree-sitter + 12 language grammars) via pip
3. Verify tree-sitter is importable

### Updating

```bash
cd ~/Projects/claude-config
git pull
./install.sh
```

Since skills are symlinked, pulling updates is usually enough. Re-run `install.sh` only if new skills were added or Python dependencies changed.

## Usage

### Available Skills (10)

| Skill | Command | Type | Description |
|-------|---------|------|-------------|
| Onboard | `/onboard` | Script-backed | Runs tree-sitter analysis on the current project, generates architecture overview and code smell report |
| AAP | `/aap <file>` | Script-backed | Parses Agent Action Plan documents for structure validation, consistency checks, LoC estimation |
| Tech Spec | `/tech-spec <file>` | Script-backed | Parses Technical Specifications for completeness, architecture consistency, risk assessment |
| README | `/readme` | Prompt-only | Auto-detects project metadata and generates/updates README.md following ClearDocs styling |
| Commit | `/commit` | Prompt-only | Stages and commits with conventional commit messages, branch safety, sensitive file detection |
| Lint | `/lint` | Prompt-only | Reviews code changes for bugs, security vulnerabilities, performance issues, style drift |
| Test | `/test` | Prompt-only | Generates and runs tests for specified files, auto-detecting test framework and conventions |
| Dev Doc | `/dev-doc` | Prompt-only | Cleans and standardizes Mintlify documentation pages to match Blitzy docs conventions |
| Z | `/z` | Prompt-only | Generates structured Blitzy prompts through category-adaptive requirements gathering |

### Skill Flags

**`/onboard`** — Codebase architecture and smell analysis
- `--skip-smells TYPE,TYPE` — Exclude specific smell types
- `--long-func N` — Override lines threshold (default: 50)
- `--skip-dirs dir,dir` — Additional directories to ignore

**`/aap <file>`** — Agent Action Plan reviewer
- `--loc-create N`, `--loc-modify N` — Override LoC estimates
- `--verbose` — Include full heading dump
- `--focus AREA` — Focus on: `frontend`, `backend`, `rules`, `scope`, `deps`, `integration`

**`/tech-spec <file>`** — Technical Specification reviewer
- `--verbose` — Include full section dump
- `--focus AREA` — Focus on: `requirements`, `architecture`, `technology`, `scope`, `integration`, `infrastructure`

**`/readme`** — ClearDocs README generator
- `--minimal` — Name, description, install, usage only
- `--internal` — Omit Contributing, Contact, License
- `--library` — Add API Reference and Changelog sections

**`/commit`** — Conventional commit helper
- `--amend` — Amend previous commit
- `--quick` — Skip confirmation, auto-commit
- `--wip` — Create work-in-progress commit
- `--fixes #N`, `--closes #N` — Link to issue

**`/lint`** — Multi-category code review
- `--pr N` — Review a GitHub PR by number
- `--staged` — Only review staged changes
- `--security` — Deep security-focused review
- `--base <branch>` — Compare against specific branch

**`/test`** — Framework-aware test generator
- `--framework <name>` — Override auto-detection
- `--update` — Update existing tests
- `--run` — Run tests after generation
- `--coverage` — Include coverage reporting

### Adding a New Skill

1. Create a directory under `skills/`:
   ```
   skills/my-skill/
   └── SKILL.md
   ```
2. Write `SKILL.md` with YAML frontmatter (`name`, `description`, `allowed-tools`)
3. Add the skill name to the `SKILLS` array in `install.sh`
4. Re-run `./install.sh`

## Structure

```
claude-config/
├── install.sh                 # Symlink installer + pip dependency setup
├── requirements.txt           # Python deps (tree-sitter + 12 language grammars)
├── README.md                  # This file
└── skills/
    ├── onboard/               # /onboard — codebase architecture & smell analysis
    │   ├── SKILL.md
    │   └── scripts/
    │       └── treemap.py     # Tree-sitter structural mapper + smell detector
    ├── aap/                   # /aap — Agent Action Plan reviewer
    │   ├── SKILL.md
    │   └── scripts/
    │       └── aap_parser.py  # Tree-sitter AAP document parser
    ├── tech-spec/             # /tech-spec — Technical Specification reviewer
    │   ├── SKILL.md
    │   └── scripts/
    │       └── tech_spec_parser.py  # Tree-sitter tech spec parser
    ├── readme/                # /readme — ClearDocs README generator
    │   └── SKILL.md
    ├── commit/                # /commit — conventional commit helper
    │   └── SKILL.md
    ├── lint/                  # /lint — multi-category code review
    │   └── SKILL.md
    ├── test/                  # /test — framework-aware test generator
    │   └── SKILL.md
    ├── dev-doc/               # /dev-doc — Mintlify docs standardization
    │   └── SKILL.md
    └── z/                     # /z — Blitzy prompt generator
        └── SKILL.md
```

### Key Files

- **`install.sh`** — Bash installer that symlinks skill directories into `~/.claude/skills/` and installs Python dependencies. Edit the `SKILLS` array to register new skills.
- **`skills/onboard/scripts/treemap.py`** — Tree-sitter codebase mapper supporting 11 languages. Uses visitor pattern for AST traversal and smell detection.
- **`skills/aap/scripts/aap_parser.py`** — Tree-sitter markdown parser for AAP documents. Extracts headings, tables, rules, and scope items.
- **`skills/tech-spec/scripts/tech_spec_parser.py`** — Tree-sitter markdown parser for Technical Specifications. Extracts features, components, technologies, and integration points.

## Tasks

- [ ] Add a LICENSE file
- [ ] Add unit tests for parser scripts
- [ ] Extract shared visitor pattern infrastructure into `skills/shared/markdown_parser.py`

## Contributing

Contributions make the open source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit your Changes (`git commit -m 'Add amazing feature'`)
4. Push to the Branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Contact

Michael Montanaro

Project Link: [https://github.com/montymi/claude-config](https://github.com/montymi/claude-config)

## Acknowledgments

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic
- [tree-sitter](https://tree-sitter.github.io/tree-sitter/) for structural code parsing
- [shields.io](https://shields.io/) for README badges

---

<!-- Reference-style links -->
[contributors-shield]: https://img.shields.io/github/contributors/montymi/claude-config.svg?style=flat
[contributors-url]: https://github.com/montymi/claude-config/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/montymi/claude-config.svg?style=flat
[forks-url]: https://github.com/montymi/claude-config/network/members
[stars-shield]: https://img.shields.io/github/stars/montymi/claude-config.svg?style=flat
[stars-url]: https://github.com/montymi/claude-config/stargazers
[issues-shield]: https://img.shields.io/github/issues/montymi/claude-config.svg?style=flat
[issues-url]: https://github.com/montymi/claude-config/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-blue.svg?style=flat&logo=linkedin
[linkedin-url]: https://linkedin.com/in/michael-montanaro
[python-shield]: https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white
[python-url]: https://python.org
[bash-shield]: https://img.shields.io/badge/Bash-4EAA25?style=flat&logo=gnubash&logoColor=white
[bash-url]: https://www.gnu.org/software/bash/
