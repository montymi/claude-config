---
name: readme
description: Create or update a README.md following ClearDocs styling principles
allowed-tools: [Read, Write, Edit, Glob, Grep, "Bash(git remote:*)", "Bash(git config:*)"]
---

# README Generator — ClearDocs Style

You are generating or updating a `README.md` for the current project using the ClearDocs template structure.

## Pre-flight Check

**Check if the project has been onboarded** by looking for project memory files in Claude's auto memory directory (`.claude/projects/.../memory/MEMORY.md`). If memory files exist, use them as a primary source for the "About" and "Architecture" sections. If no memory files exist, inform the user:

> "This project hasn't been onboarded yet. I'll do my best from the source files, but consider running `/onboard` first for richer output."

## Arguments

`$ARGUMENTS` may contain:
- A GitHub `owner/repo` string (e.g., `mmontanaro/mistral-vibe`) — use this for shields.io URLs
- `--update` — only update existing sections, don't overwrite custom content
- If empty, auto-detect everything

## Step 1: Auto-detect Project Metadata

Gather as much as possible automatically:

1. **GitHub owner/repo** — parse from `$ARGUMENTS`, or run `git remote get-url origin` and extract from the URL
2. **Project name** — from `package.json` `name`, `pyproject.toml` `[project] name`, `Cargo.toml` `[package] name`, `go.mod` module path, or the repository directory name
3. **Description** — from `package.json` `description`, `pyproject.toml` `[project] description`, or onboard memory
4. **License** — read `LICENSE` or `LICENSE.md` file, or check `package.json` / `pyproject.toml`
5. **Tech stack** — detect from:
   - `package.json` / `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` → Node.js ecosystem
   - `pyproject.toml` / `setup.py` / `setup.cfg` / `requirements.txt` / `Pipfile` → Python ecosystem
   - `Cargo.toml` → Rust
   - `go.mod` → Go
   - `Gemfile` → Ruby
   - `pom.xml` / `build.gradle` → Java
   - Key dependencies (React, Vue, Django, FastAPI, etc.) from dependency files
6. **Author** — from git config, `package.json`, or `pyproject.toml`. Default to "Michael Montanaro" if undetectable
7. **Installation method** — detect from `Makefile`, `Dockerfile`, lockfiles, `setup.py`, etc.

## Step 2: Read Existing README (if present)

If a `README.md` already exists:
1. Read its full contents
2. Identify any custom sections or content not part of the ClearDocs template
3. Preserve custom content by integrating it into the appropriate ClearDocs section
4. Note what needs updating vs. what should be left alone

## Step 3: Generate README.md

Write the README using this exact structure. Use `OWNER`, `REPO`, `PROJECT_NAME`, etc. as detected above. All shields.io badge URLs must use **reference-style links** defined at the bottom of the file.

### Template Structure

```markdown
<!-- Shields bar -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- Project header -->
<div align="center">
  <h1>PROJECT_NAME</h1>
  <p>PROJECT_DESCRIPTION</p>
  <a href="https://github.com/OWNER/REPO"><strong>Explore the docs</strong></a>
  &middot;
  <a href="https://github.com/OWNER/REPO/issues/new?labels=bug">Report Bug</a>
  &middot;
  <a href="https://github.com/OWNER/REPO/issues/new?labels=enhancement">Request Feature</a>
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

[Description from onboard memory, pyproject.toml, or user prompt. 2-4 paragraphs covering what the project does, why it exists, and who it's for.]

## Built With

[Shields.io badges for each major technology detected. Use flat-style badges.]

Example:
[![Python][python-shield]][python-url]
[![React][react-shield]][react-url]

## Getting Started

### Prerequisites

[List runtime requirements detected from the project]

### Installation

[Step-by-step install commands detected from Makefile, lockfiles, setup.py, etc.]

## Usage

[CLI examples, API usage, or code snippets. Pull from onboard memory if available, otherwise provide placeholder with TODO.]

## Structure

[Directory tree or architecture overview. If onboard memory exists, use its architecture summary. Otherwise, generate a high-level tree.]

## Tasks

- [ ] [Open TODOs from issues or code — placeholder if none detected]

## Contributing

Contributions make the open source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit your Changes (`git commit -m 'Add amazing feature'`)
4. Push to the Branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the [DETECTED_LICENSE] License. See `LICENSE` for more information.

## Contact

AUTHOR_NAME — AUTHOR_LINK

Project Link: [https://github.com/OWNER/REPO](https://github.com/OWNER/REPO)

## Acknowledgments

- []

---

<!-- Reference-style links -->
[contributors-shield]: https://img.shields.io/github/contributors/OWNER/REPO.svg?style=flat
[contributors-url]: https://github.com/OWNER/REPO/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/OWNER/REPO.svg?style=flat
[forks-url]: https://github.com/OWNER/REPO/network/members
[stars-shield]: https://img.shields.io/github/stars/OWNER/REPO.svg?style=flat
[stars-url]: https://github.com/OWNER/REPO/stargazers
[issues-shield]: https://img.shields.io/github/issues/OWNER/REPO.svg?style=flat
[issues-url]: https://github.com/OWNER/REPO/issues
[license-shield]: https://img.shields.io/github/license/OWNER/REPO.svg?style=flat
[license-url]: https://github.com/OWNER/REPO/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-blue.svg?style=flat&logo=linkedin
[linkedin-url]: https://linkedin.com/in/LINKEDIN_USERNAME
```

### Badge References for Common Tech

Add these to the reference-style links footer as needed:

```
[python-shield]: https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white
[python-url]: https://python.org
[javascript-shield]: https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black
[javascript-url]: https://developer.mozilla.org/en-US/docs/Web/JavaScript
[typescript-shield]: https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white
[typescript-url]: https://typescriptlang.org
[react-shield]: https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black
[react-url]: https://react.dev
[next-shield]: https://img.shields.io/badge/Next.js-000000?style=flat&logo=next.js&logoColor=white
[next-url]: https://nextjs.org
[vue-shield]: https://img.shields.io/badge/Vue.js-4FC08D?style=flat&logo=vue.js&logoColor=white
[vue-url]: https://vuejs.org
[rust-shield]: https://img.shields.io/badge/Rust-000000?style=flat&logo=rust&logoColor=white
[rust-url]: https://rust-lang.org
[go-shield]: https://img.shields.io/badge/Go-00ADD8?style=flat&logo=go&logoColor=white
[go-url]: https://go.dev
[django-shield]: https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white
[django-url]: https://djangoproject.com
[fastapi-shield]: https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white
[fastapi-url]: https://fastapi.tiangolo.com
[node-shield]: https://img.shields.io/badge/Node.js-339933?style=flat&logo=node.js&logoColor=white
[node-url]: https://nodejs.org
[docker-shield]: https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white
[docker-url]: https://docker.com
```

## Formatting Rules

- Replace ALL placeholder values (`OWNER`, `REPO`, `PROJECT_NAME`, etc.) with detected values
- If a value can't be detected, use a sensible placeholder wrapped in `<!-- TODO: ... -->` comments
- All shields.io URLs go in the reference-style links footer — never inline
- Use HTML sparingly (only for centering the header and the collapsible TOC)
- Keep the markdown clean and readable in source form
- Ensure all anchor links in the TOC match the actual heading IDs
