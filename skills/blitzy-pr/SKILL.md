---
name: blitzy-pr
description: Validate a PR by running the developer onboarding checklist from the Blitzy Project Guide Section 9
allowed-tools: [Read, Glob, Grep, Bash]
---

# Blitzy PR — Developer Onboarding Validation

You are validating a PR by executing the developer onboarding steps from the Blitzy Project Guide.

## Step 1: Load the Project Guide

Read `blitzy/documentation/projectguide.md` and navigate to **Section 9** (the developer onboarding section).

## Step 2: Execute the Onboarding Checklist

Follow Section 9 **command by command**, in order. For each step:

1. Run the exact command specified in the guide
2. Record whether it passed or failed
3. If a step fails, capture the error output and continue to the next step

Do not skip steps. Do not reorder steps. Do not add steps that are not in the guide.

## Step 3: Report Results

Present results as a checklist:

```
## PR Validation Results

| # | Step | Command | Status | Notes |
|---|------|---------|--------|-------|
| 1 | ... | `...` | PASS/FAIL | ... |
| 2 | ... | `...` | PASS/FAIL | ... |
| ... | | | | |

**Result:** [ALL PASS | N FAILURES]
```

If any step failed, include the relevant error output below the table.
