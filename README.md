# claude-config

Personal Claude Code skills and configuration, version-controlled and portable across machines.

## What's Inside

```
claude-config/
├── install.sh             # Symlink installer
├── requirements.txt       # Python deps for tree-sitter
├── skills/
│   ├── onboard/           # /onboard — codebase architecture & smell analysis
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── treemap.py # Tree-sitter structural mapper
│   └── readme/            # /readme — ClearDocs README generator
│       └── SKILL.md
```

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed (`~/.claude/` must exist)
- Python 3.10+
- git

## Installation

```bash
git clone https://github.com/mmontanaro/claude-config.git ~/Projects/claude-config
cd ~/Projects/claude-config
chmod +x install.sh
./install.sh
```

The installer will:
1. Symlink each skill directory into `~/.claude/skills/`
2. Install Python dependencies (tree-sitter grammars) via pip

## Available Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Onboard | `/onboard` | Runs tree-sitter analysis on the current project, generates an architecture overview, code smell report, and saves findings to Claude's project memory |
| README | `/readme` | Auto-detects project metadata and generates/updates a README.md following ClearDocs styling (shields.io badges, structured sections, reference-style links) |

## Adding a New Skill

1. Create a directory under `skills/`:
   ```
   skills/my-skill/
   └── SKILL.md
   ```
2. Write `SKILL.md` with YAML frontmatter (`name`, `description`, `allowed-tools`)
3. Add the skill name to the `SKILLS` array in `install.sh`
4. Re-run `./install.sh`

## Updating

```bash
cd ~/Projects/claude-config
git pull
./install.sh
```

Since skills are symlinked, pulling updates is usually enough. Re-run `install.sh` only if new skills were added or Python dependencies changed.
