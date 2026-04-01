# ISDD Skill Quality Rubric

Scoring guide used by the `skill-review` skill for evaluating Claude Code skills.

## Dimensions (each 0–2 points, total /10)

### 1. Frontmatter completeness (0–2)
- **2**: All relevant fields present and correctly formed
- **1**: Minor issues (description slightly over 250 chars, missing argument-hint)
- **0**: Missing description, invalid YAML, unsupported keys

### 2. Description quality (0–2)
- **2**: Front-loads trigger phrases, under 250 chars, clearly states when to use
- **1**: Describes the skill but buries the trigger phrase, or is close to 250 chars
- **0**: Missing, too long, or describes what the skill is rather than when to use it

### 3. Instruction clarity (0–2)
- **2**: Imperative step-by-step instructions, unambiguous, complete
- **1**: Some steps are vague or passive ("the skill will do X")
- **0**: Instructions are descriptive-only, circular, or incomplete

### 4. Security hygiene (0–2)
- **2**: Minimal tool permissions, side-effect skills have disable-model-invocation
- **1**: Slightly over-permissioned or missing disable-model-invocation for borderline side effects
- **0**: Unnecessary Bash/Write access, no disable-model-invocation for destructive skills

### 5. Marketplace readiness (0–2)
- **2**: Valid plugin.json entry, version in marketplace.json only, CHANGELOG exists
- **1**: plugin.json entry exists but version also in plugin.json (override risk)
- **0**: No plugin.json entry, no versioning, no documentation

## Score interpretation

| Score | Status |
|-------|--------|
| 9–10 | Publish-ready |
| 7–8 | Minor revisions needed |
| 5–6 | Significant revisions needed |
| Below 5 | Rewrite recommended |
