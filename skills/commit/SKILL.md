---
name: commit
description: Stage and commit changes with conventional commit messages, with branch safety and auto-generated messages
allowed-tools: [Glob, Grep, Read, "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(git branch:*)", "Bash(git checkout:*)", "Bash(git switch:*)", "Bash(git add:*)", "Bash(git commit:*)", "Bash(git rev-parse:*)", "Bash(git stash:*)"]
---

# Commit — Conventional Commits with Branch Safety

You are staging and committing changes in a git repository using conventional commit conventions.

## Step 1: Pre-flight Checks

1. Run `git rev-parse --is-inside-work-tree` to confirm this is a git repo. If not, stop and tell the user.
2. Run `git status --porcelain` to check for changes. If there are no staged, unstaged, or untracked changes, stop and tell the user there's nothing to commit.
3. Check for detached HEAD with `git rev-parse --abbrev-ref HEAD`. If it returns `HEAD`, warn the user they're in detached HEAD state and ask how to proceed.

## Step 2: Branch Safety

1. Get the current branch: `git rev-parse --abbrev-ref HEAD`
2. If the branch is any of: `main`, `master`, `develop`, `development`, `qa`, `prod`, `production`, `staging`, `release` — **warn the user** that they're on a protected branch.
3. Ask the user for a branch name, suggesting one based on the changes (see Step 3 for naming convention).
4. Create the branch with `git checkout -b <branch-name>`.
5. If the user explicitly says they want to commit directly to the protected branch, proceed — but confirm once more before committing.

## Step 3: Branch Naming Convention

When suggesting or creating branches, use this format:

```
<type>/<kebab-case-description>
```

- **Type** matches the conventional commit type: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `style`, `perf`, `ci`, `build`
- **Description**: 2-5 words, kebab-case, under 60 chars total
- Examples: `feat/add-user-auth`, `fix/null-check-parser`, `docs/update-api-reference`, `chore/bump-dependencies`

## Step 4: Analyze Changes

Run these commands to understand the full picture:

1. `git diff` — unstaged changes
2. `git diff --cached` — staged changes
3. `git status --porcelain` — all changes including untracked files

If diffs are large, read key changed files to understand the nature of the changes.

## Step 5: Safety Scan

Check for sensitive files in the changeset. **Warn and exclude** any of these:

- `.env`, `.env.*` (environment variables)
- `*.pem`, `*.key`, `*.p12`, `*.pfx` (certificates/keys)
- `credentials.json`, `service-account.json` (API credentials)
- `id_rsa`, `id_ed25519`, `*.pub` (SSH keys)
- `*.sqlite`, `*.db` (databases)
- `.npmrc`, `.pypirc` (package registry auth)
- `*.secret`, `*_secret*`

If any are found:
1. Tell the user which files were excluded and why
2. Suggest adding them to `.gitignore` if not already present
3. Proceed with the remaining files

## Step 6: Stage Files

- Use `git add <file1> <file2> ...` with explicit file paths. **Never** use `git add -A` or `git add .`.
- If there are already staged changes and no unstaged changes, skip staging and use what's already staged.
- If there are both staged and unstaged changes, ask the user whether to include the unstaged changes or commit only what's staged.
- If there are more than 15 files to stage, list them and confirm with the user before staging.

## Step 7: Determine Commit Message

### If `$ARGUMENTS` is provided:
- If it's already in conventional commit format (e.g., `fix: resolve null pointer`), use it as-is.
- If it's a plain description (e.g., `fix the login bug`), convert it to conventional format.

### If `$ARGUMENTS` is empty:
Auto-detect the commit type from the diff:

| Type | Heuristic |
|------|-----------|
| `feat` | New files, new functions/methods/components, new exports |
| `fix` | Changes to existing logic, error handling, edge cases |
| `refactor` | Restructuring without behavior change, renames, moves |
| `docs` | Only `.md` files, comments, or docstrings changed |
| `chore` | Dependency updates, config files, maintenance |
| `test` | Test files added or modified |
| `style` | Formatting, whitespace, linting fixes |
| `perf` | Optimization, caching, reducing allocations |
| `ci` | CI/CD config files (`.github/workflows`, Jenkinsfile, etc.) |
| `build` | Build scripts, Dockerfile, Makefile changes |

### Message format:
```
<type>(<optional-scope>): <imperative-description>
```

- Use **imperative mood** ("add", "fix", "update" — not "added", "fixes", "updated")
- **Lowercase** first word after the colon
- **No period** at the end
- Keep the subject line **under 50 characters**
- Add a **body** (separated by blank line) for non-trivial changes explaining *why*, not *what*

## Step 8: Confirm and Commit

Present a summary to the user:

```
Branch:  <branch-name>
Staged:  <number> file(s)
Message: <proposed commit message>

Files:
  - path/to/file1.ts
  - path/to/file2.ts
```

- Wait for the user to approve, edit the message, or cancel.
- Execute the commit using a heredoc for proper formatting:
  ```
  git commit -m "$(cat <<'EOF'
  <type>(<scope>): <description>

  <optional body>
  EOF
  )"
  ```
- Verify with `git log --oneline -1`.

## Step 9: Post-commit Summary

After a successful commit, show:

```
Committed: <short-hash> <commit message>
Branch:    <branch-name>
Files:     <count> changed
```

Then suggest: "Run `git push` to push your changes." — but **do not execute `git push`**.

## Edge Cases

- **Only staged changes**: Skip staging, commit what's already staged.
- **Mixed staged/unstaged**: Ask the user whether to include unstaged changes.
- **Merge conflicts**: If `git status` shows merge conflicts, tell the user to resolve them first.
- **Untracked files only**: Ask the user which files to add.
- **Detached HEAD**: Warn and ask for instructions before committing.
- **Empty diff after staging**: If staged changes result in no diff (e.g., only whitespace), warn the user.
