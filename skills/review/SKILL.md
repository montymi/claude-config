---
name: review
description: Review code changes for bugs, security vulnerabilities, performance issues, and style drift
allowed-tools: [Read, Glob, Grep, "Bash(git diff:*)", "Bash(git status:*)", "Bash(git log:*)", "Bash(git rev-parse:*)", "Bash(git branch:*)", "Bash(git show:*)", "Bash(gh pr view:*)", "Bash(gh pr diff:*)"]
---

# Code Review — Multi-Category Change Analysis

You are reviewing code changes in a git repository for correctness, security, performance, and style.

## Arguments

`$ARGUMENTS` may contain any combination of:

| Flag | Effect |
|------|--------|
| `--pr N` | Review a GitHub PR by number |
| `--staged` | Only review staged changes |
| `--security` | Security-focused review (injection, auth, secrets, data exposure) |
| `--base <branch>` | Compare against a specific branch instead of HEAD |
| *(plain text)* | Additional context about the intent of the changes |

## Step 1: Determine Review Scope

Identify what to review based on arguments:

1. **`--pr N`** — Run `gh pr view N --json number,title,body,baseRefName,headRefName` and `gh pr diff N` to get the PR metadata and diff.
2. **`--staged`** — Run `git diff --cached` to review only staged changes.
3. **`--base <branch>`** — Run `git diff <branch>...HEAD` to compare the current branch against the specified base.
4. **Default** (no flags) — Run `git diff` for unstaged changes. If empty, fall back to `git diff --cached` for staged changes. If both are empty, fall back to `git diff HEAD~1` for the last commit.

If there are no changes to review at any level, tell the user and stop.

Run `git status --porcelain` to get the full picture of the working tree state.

## Step 2: Gather Full File Context

For each file in the diff:

1. Read the **entire file** using the Read tool — not just the diff hunks. This catches:
   - Invariant violations (changing behavior that callers depend on)
   - Missing imports for newly used symbols
   - Uninitialized variables referenced later in the file
   - Broken consistency with other functions in the same file
2. For renamed or moved files, read both the old and new paths if available.
3. If a diff touches more than 20 files, prioritize:
   - Source code over config/lockfiles
   - Files with logic changes over files with only formatting changes
   - Read at least the first 10 most-changed source files in full

## Step 3: Analyze Project Conventions

Before reviewing, understand the project's standards:

1. **Language and framework** — detect from file extensions, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.
2. **Linting config** — check for `.eslintrc*`, `pyproject.toml [tool.ruff]`, `rustfmt.toml`, `.prettierrc`, `.editorconfig`, `biome.json`, etc.
3. **Existing patterns** — read 1-2 similar files (same directory or same type) to understand naming conventions, error handling style, and code organization patterns already in use.

## Step 4: Perform Review

Analyze the changes across these categories:

### 4a. Correctness & Bugs
- Logic errors, off-by-one, null/undefined access
- Race conditions, missing awaits, unhandled promises
- Incorrect type usage, wrong comparisons
- Missing error handling for operations that can fail
- State mutations that break assumptions elsewhere

### 4b. Security
- **Always check**: hardcoded secrets, credentials in code, SQL/command injection, path traversal
- **With `--security`**: perform deeper analysis:
  - Authentication and authorization gaps
  - Input validation and sanitization
  - XSS, CSRF, SSRF vectors
  - Insecure deserialization
  - Data exposure in logs, error messages, or API responses
  - Dependency vulnerabilities (known CVEs in added packages)
  - Timing attacks on security-sensitive comparisons

### 4c. Performance
- Unnecessary allocations in hot paths
- N+1 query patterns
- Missing indexes suggested by new queries
- Unbounded loops or recursive calls without limits
- Large objects passed by value when reference would suffice
- Missing caching for repeated expensive operations

### 4d. Edge Cases
- Empty inputs, zero values, negative numbers
- Unicode and encoding issues
- Concurrent access to shared state
- Boundary conditions at limits (max int, empty collections, single-element lists)
- Network/IO failures, timeouts, partial writes

### 4e. Style & Maintainability
- Naming that doesn't match project conventions
- Dead code, commented-out code, TODO comments without issue links
- Functions that are too long or do too many things
- Missing or misleading documentation on public APIs
- Inconsistent patterns compared to the rest of the codebase

### 4f. Missing Tests
- New public functions without test coverage
- Bug fixes without regression tests
- Changed behavior without updated tests
- Edge cases identified above that should be tested

## Step 5: Present Findings

Format each finding as:

```
### [SEVERITY] Category — Brief title

**File:** `path/to/file.ext:LINE`

**Issue:** Clear explanation of what's wrong and why it matters.

**Fix:**
\`\`\`LANG
// concrete code fix or suggestion
\`\`\`
```

### Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **Critical** | Bugs, security vulnerabilities, data loss risks | Must fix before merging |
| **Warning** | Performance issues, error handling gaps, potential edge case failures | Should fix, may be acceptable with justification |
| **Suggestion** | Better patterns, readability improvements, minor optimizations | Nice to have, author's discretion |
| **Nitpick** | Style preferences, naming alternatives, minor formatting | Informational only |

### Ordering

Present findings in severity order: Critical first, then Warning, Suggestion, Nitpick.

## Step 6: Summary & Verdict

End the review with a summary:

```
---

## Review Summary

| Category | Critical | Warning | Suggestion | Nitpick |
|----------|----------|---------|------------|---------|
| Correctness | N | N | N | N |
| Security | N | N | N | N |
| Performance | N | N | N | N |
| Edge Cases | N | N | N | N |
| Style | N | N | N | N |
| Tests | N | N | N | N |

**Verdict:** [Approve | Request Changes | Comment]

[One-sentence summary of the overall assessment]
```

### Verdict Rules

- **Approve** — No critical or warning findings. All changes are correct and follow project conventions.
- **Request Changes** — Any critical finding, or 3+ warnings. Changes should be addressed before merging.
- **Comment** — Warnings exist but are minor, or only suggestions/nitpicks. Safe to merge but improvements are recommended.

## Composability

After the review, suggest next steps when relevant:

- If missing test coverage was identified: "Consider running `/test <file>` to generate tests for uncovered code."
- If fixes are needed and the user makes them: "Run `/commit --quick` to commit the fixes."
- If reviewing a PR: "Use `gh pr review N --approve` or `gh pr review N --request-changes` to submit your review on GitHub."

## Edge Cases

- **Binary files in diff**: Skip binary files, note them as "skipped (binary)".
- **Generated files**: Skip files that appear auto-generated (lockfiles, `.min.js`, compiled output, `*.pb.go`, etc.). Note them as "skipped (generated)".
- **Very large diffs** (50+ files): Summarize the scope, then focus the detailed review on the most impactful files. List skipped files at the end.
- **No changes found**: Tell the user there's nothing to review and suggest checking `git status`.
- **Merge conflicts**: If the diff contains conflict markers, tell the user to resolve conflicts before requesting a review.
