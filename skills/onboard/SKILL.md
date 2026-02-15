---
name: onboard
description: Generate an architecture overview and onboarding guide using tree-sitter codebase mapping and code smell detection
disable-model-invocation: true
context: fork
agent: Explore
---

# Onboard — Codebase Architecture & Smell Analysis

You are generating an onboarding guide for a codebase. A tree-sitter structural map and code smell report have been injected below.

## Injected Data

```
!`python3 ~/.claude/skills/onboard/scripts/treemap.py`
```

## Your Task

Using the structural map and smell report above, produce a comprehensive onboarding document with these sections:

### 1. Architecture Overview
- High-level description of the project's purpose and design
- Key directories and what they contain
- Layering / module boundaries (e.g., CLI vs core vs API)

### 2. Entry Points
- Where execution starts (main functions, CLI entry points, app factories)
- How a request/command flows through the system

### 3. Key Abstractions
- The most important classes, interfaces, and types
- How they relate to each other (inheritance, composition, dependency)

### 4. Data Flow
- How data moves through the system (user input -> processing -> output)
- Key data structures and where they're transformed

### 5. Import / Dependency Graph
- Which modules depend on which
- Any notable patterns (layered architecture, plugin system, etc.)

### 6. Code Smells & Tech Debt (Prioritized)
- Walk through each smell from the report
- Group by severity (High / Medium / Low)
- For each, briefly explain *why* it's a problem and suggest a concrete fix
- If circular imports were detected, explain the cycle and how to break it

### 7. Onboarding Recommendations
- Suggested reading order for a new contributor
- Files to read first to understand the architecture
- Common patterns used in the codebase
- Gotchas and non-obvious conventions

### 8. Save to Project Memory
After generating the onboarding document, **persist the key findings** to Claude's project memory so future sessions benefit automatically.

**First, check if the project has already been onboarded** by reading the existing `MEMORY.md` in the project's auto memory directory (`.claude/projects/.../memory/MEMORY.md`).

#### If MEMORY.md already exists (re-onboarding):
1. Read all existing memory files to understand what's already saved
2. Compare the previous onboarded commit hash with the current HEAD
3. **Preserve** any user-added notes, preferences, or debugging insights that aren't part of the auto-generated onboarding sections
4. **Update** the architecture sections with new findings from the fresh tree-sitter analysis
5. **Add a re-onboard note** at the top of MEMORY.md: `Re-onboarded at commit <hash> (previously <old-hash>)`
6. **Highlight what changed** — new files/modules, removed modules, new or resolved code smells, shifted architecture
7. If the codebase structure hasn't materially changed, keep updates minimal and preserve existing memory content

#### If MEMORY.md does not exist (first onboarding):
1. Note the **Git HEAD commit hash** printed at the top of the injected data
2. Write a concise `MEMORY.md` containing:
   - Project overview (1-2 sentences)
   - Onboarded commit hash
   - Key entry points
   - Core abstractions (names and file paths)
   - Data flow summary
   - Known tech debt highlights
3. Create additional topic files (e.g., `architecture.md`, `key-files.md`) linked from MEMORY.md for detailed reference

#### Always:
- Keep MEMORY.md under 200 lines (it gets loaded into the system prompt)
- Use topic files for detailed content, link from MEMORY.md

## Formatting Rules
- Use markdown headers and bullet points
- Reference specific files and line numbers from the map
- Keep the document scannable — use bold for key terms
- Be direct and specific, not generic
