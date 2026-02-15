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
  <a href="https://github.com/mmontanaro/claude-config"><strong>Explore the docs</strong></a>
  &middot;
  <a href="https://github.com/mmontanaro/claude-config/issues/new?labels=bug">Report Bug</a>
  &middot;
  <a href="https://github.com/mmontanaro/claude-config/issues/new?labels=enhancement">Request Feature</a>
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
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

---

## About The Project

claude-config is a version-controlled collection of custom [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills and configuration. It provides portable, reusable slash commands that extend Claude Code with project-specific workflows like codebase onboarding and README generation.

The goal is to keep Claude Code customizations in a single repository that can be cloned onto any machine, symlinked into `~/.claude/skills/`, and immediately available in every Claude Code session. Skills are self-contained directories with a `SKILL.md` definition file and optional supporting scripts — adding a new one is as simple as dropping a directory and re-running the installer.

The `/onboard` skill uses [tree-sitter](https://tree-sitter.github.io/tree-sitter/) to parse source code across 8 languages, extract structural maps (classes, functions, imports), and detect code smells like god classes, deep nesting, and circular imports. The `/readme` skill auto-detects project metadata and generates documentation following a consistent ClearDocs template.

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
git clone https://github.com/mmontanaro/claude-config.git ~/Projects/claude-config
cd ~/Projects/claude-config
chmod +x install.sh
./install.sh
```

The installer will:
1. Symlink each skill directory into `~/.claude/skills/`
2. Install Python dependencies (tree-sitter grammars) via pip

### Updating

```bash
cd ~/Projects/claude-config
git pull
./install.sh
```

Since skills are symlinked, pulling updates is usually enough. Re-run `install.sh` only if new skills were added or Python dependencies changed.

## Usage

### Available Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Onboard | `/onboard` | Runs tree-sitter analysis on the current project, generates an architecture overview, code smell report, and saves findings to Claude's project memory |
| README | `/readme` | Auto-detects project metadata and generates/updates a README.md following ClearDocs styling (shields.io badges, structured sections, reference-style links) |

### How `/onboard` Works

1. Claude executes `treemap.py` against the current project directory
2. The script walks the filesystem, parses source files with tree-sitter, and extracts classes, functions, imports, and interfaces
3. It detects code smells: god classes (>15 methods), long functions (>50 lines), deep nesting (>4 levels), too many parameters (>5), catch-all exceptions, circular imports, and large files (>500 lines)
4. Claude receives the structural map and smell report, then generates a comprehensive onboarding document
5. Key findings are persisted to Claude's project memory for future sessions

### How `/readme` Works

1. Claude checks for onboard memory to use as context
2. It auto-detects project metadata: name, description, tech stack, license, author, and installation method
3. If a README exists, custom content is preserved and integrated
4. A ClearDocs-styled README is generated with shields.io badges and reference-style links

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
├── requirements.txt           # Python deps (tree-sitter + 7 language grammars)
├── README.md                  # This file
└── skills/
    ├── onboard/               # /onboard — codebase architecture & smell analysis
    │   ├── SKILL.md           # Skill definition (YAML frontmatter + prompt)
    │   └── scripts/
    │       └── treemap.py     # Tree-sitter structural mapper + smell detector
    └── readme/                # /readme — ClearDocs README generator
        └── SKILL.md           # Skill definition (prompt-only, no scripts)
```

### Key Files

- **`install.sh`** — Bash installer that symlinks skill directories into `~/.claude/skills/` and installs Python dependencies. Edit the `SKILLS` array to register new skills.
- **`skills/onboard/SKILL.md`** — Skill definition for `/onboard`; invokes `treemap.py` via embedded command (`` `!python3 ...` ``) and instructs Claude to generate an architecture overview.
- **`skills/onboard/scripts/treemap.py`** — Tree-sitter codebase mapper supporting Python, JavaScript, TypeScript, Rust, Go, Java, and Ruby. Core class: `CodebaseMapper`. Detects god classes, long functions, deep nesting, catch-all exceptions, circular imports, and more.
- **`skills/readme/SKILL.md`** — Skill definition for `/readme`; auto-detects project metadata and generates a ClearDocs-styled README with shields.io badges and reference-style links.

## Tasks

- [ ] Add a LICENSE file
- [ ] Set up a git remote (`origin`)
- [ ] Add unit tests for `treemap.py` smell detection logic
- [ ] Consider adding more skills (e.g., `/review`, `/changelog`)

## Contributing

Contributions make the open source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit your Changes (`git commit -m 'Add amazing feature'`)
4. Push to the Branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

<!-- TODO: Add a LICENSE file to the repository -->
No license specified yet. See the [Tasks](#tasks) section.

## Contact

Michael Montanaro

Project Link: [https://github.com/mmontanaro/claude-config](https://github.com/mmontanaro/claude-config)

## Acknowledgments

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic
- [tree-sitter](https://tree-sitter.github.io/tree-sitter/) for structural code parsing
- [shields.io](https://shields.io/) for README badges

---

<!-- Reference-style links -->
[contributors-shield]: https://img.shields.io/github/contributors/mmontanaro/claude-config.svg?style=flat
[contributors-url]: https://github.com/mmontanaro/claude-config/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/mmontanaro/claude-config.svg?style=flat
[forks-url]: https://github.com/mmontanaro/claude-config/network/members
[stars-shield]: https://img.shields.io/github/stars/mmontanaro/claude-config.svg?style=flat
[stars-url]: https://github.com/mmontanaro/claude-config/stargazers
[issues-shield]: https://img.shields.io/github/issues/mmontanaro/claude-config.svg?style=flat
[issues-url]: https://github.com/mmontanaro/claude-config/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-blue.svg?style=flat&logo=linkedin
<!-- TODO: Replace with your LinkedIn username -->
[linkedin-url]: https://linkedin.com/in/mmontanaro
[python-shield]: https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white
[python-url]: https://python.org
[bash-shield]: https://img.shields.io/badge/Bash-4EAA25?style=flat&logo=gnubash&logoColor=white
[bash-url]: https://www.gnu.org/software/bash/
