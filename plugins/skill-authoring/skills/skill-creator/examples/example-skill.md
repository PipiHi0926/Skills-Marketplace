# Worked Example: Creating the `code-reviewer` Skill

This example walks through the full skill-creator process for a realistic use case:
a skill that reviews code changes and provides structured feedback.

---

## Scenario

A developer on the CIM platform team wants a slash command that reviews staged
git changes and produces a structured code review with findings categorized by
severity. The review should be read-only — it should never modify files or commit
anything.

**User says:** "Create a skill for me that reviews code and gives feedback"

---

## Step 1: Gather requirements (Q&A)

| Question | Answer |
|----------|--------|
| Skill name? | `code-reviewer` |
| What does it do? | Reviews staged git diff or a specified file for bugs, style issues, and security problems |
| Auto-trigger or user-invoked? | Both — auto-trigger when user says "review my code" or "look at my changes" |
| Tools needed? | Read, Glob, Grep (no Write — purely read-only) |
| Takes arguments? | Yes — optional file path or "staged" keyword |
| Run in isolation? | No — needs conversation context to understand intent |
| Side effects? | None — read-only analysis only |

---

## Step 2: Frontmatter decisions

**`name: code-reviewer`**
Kebab-case, 13 characters — well within the 64-char limit. Becomes the `/code-reviewer` slash command.

**`description`** — front-load the trigger:
"Review code for bugs, style, and security issues. Use when: 'review my code', 'check my changes', 'look at this file for problems', or /code-reviewer [path]."
This is 173 characters — under the 250-char limit, and the trigger phrases appear early so Claude's matching works well.

**`allowed-tools: Read, Glob, Grep`**
No Write, no Bash, no ability to execute or modify anything. This enforces the read-only contract.

**`disable-model-invocation`** — NOT set (left as default `false`)
This skill has no side effects, so it's safe for Claude to invoke it automatically when it detects the trigger phrases.

**`argument-hint: "[file-path|staged]"`**
Tells the user what arguments are accepted. Square brackets indicate optional.

**`context`** — left as default `inline`
The skill benefits from conversation history (e.g., the user may have just said "I fixed the auth bug, can you review?").

---

## Step 3: The resulting SKILL.md

```markdown
---
name: code-reviewer
description: >
  Review code for bugs, style, and security issues. Use when: "review my code",
  "check my changes", "look at this file for problems", or /code-reviewer [path].
  Produces a structured report with severity-categorized findings.
argument-hint: "[file-path|staged]"
allowed-tools: Read, Glob, Grep
---

# Code Reviewer

Review the specified code or staged changes and produce a structured findings report.

## Input

Arguments: `$ARGUMENTS`

- If `$ARGUMENTS` is empty or "staged": review the most recently discussed files
  in the conversation, or ask the user which files to review.
- If `$ARGUMENTS` is a file path: read and review that file directly.
- If `$ARGUMENTS` is a glob pattern: expand and review all matching files.

## Review process

1. **Read the target file(s)** using the Read tool.
2. **Check for bugs**: logic errors, off-by-one errors, null dereferences,
   unhandled exceptions, race conditions.
3. **Check for security issues**: hardcoded secrets, SQL injection, path traversal,
   missing input validation, insecure deserialization.
4. **Check for style issues**: naming conventions, code duplication, overly complex
   functions, missing docstrings on public APIs.
5. **Check for maintainability**: magic numbers, deeply nested logic, missing
   error handling.

## Output format

Produce a structured report:

---
## Code Review: <filename>

### Summary
<One paragraph overall assessment including the most important finding>

### Findings

#### Critical (must fix before merge)
- **Line N**: <issue description> — <suggested fix>

#### Warnings (should fix)
- **Line N**: <issue description> — <suggested fix>

#### Suggestions (consider improving)
- **Line N**: <suggestion>

### Overall verdict: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION
---

If no issues are found in a category, omit that section rather than writing "None found."
```

---

## Step 4: Why each choice was made

| Decision | Rationale |
|----------|-----------|
| `allowed-tools: Read, Glob, Grep` | Read-only analysis needs only read tools. Granting Bash would let Claude accidentally run code. |
| No `disable-model-invocation` | Safe to auto-invoke — no files are modified, no commands are run. |
| No `context: fork` | Inline context lets Claude reference earlier conversation (e.g., which files the user was discussing). |
| `argument-hint: "[file-path|staged]"` | The pipe-separated hint shows both options clearly in autocomplete. |
| Output format specified in skill body | Without a specified format, Claude produces inconsistent output styles across invocations. |
| Trigger phrases in description | "review my code", "check my changes" are exactly what users type — Claude matches on these. |

---

## Step 5: File placement

For this marketplace:
```
plugins/code-review/
  .claude-plugin/
    plugin.json
  skills/
    code-reviewer/
      SKILL.md          ← the file above
  CHANGELOG.md
```

Add to `.claude-plugin/marketplace.json`:
```json
{
  "name": "code-review",
  "source": "./plugins/code-review",
  "description": "Automated code review skill for CIM teams",
  "version": "1.0.0",
  "category": "developer-tools",
  "keywords": ["code-review", "quality", "security"]
}
```

And create `plugins/code-review/.claude-plugin/plugin.json` (no version field):
```json
{
  "name": "code-review",
  "description": "Automated code review skill for CIM teams",
  "author": { "name": "CIM Platform Team" },
  "keywords": ["code-review", "quality", "security"]
}
```
