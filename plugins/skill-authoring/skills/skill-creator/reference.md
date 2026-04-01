# SKILL.md Frontmatter Reference

Complete field reference for Claude Code SKILL.md files.

## All frontmatter fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | No | Directory name | kebab-case, max 64 chars |
| `description` | Recommended | First paragraph | Trigger description, max 250 chars in listing |
| `argument-hint` | No | — | Autocomplete hint e.g. `[filename]` |
| `disable-model-invocation` | No | `false` | Prevent Claude auto-invocation |
| `user-invocable` | No | `true` | Set `false` to hide from / menu |
| `allowed-tools` | No | All | Comma-separated tool allowlist |
| `model` | No | Session default | Model override |
| `effort` | No | Session default | `low`, `medium`, `high`, `max` |
| `context` | No | inline | `fork` to run in isolated subagent |
| `agent` | No | `general-purpose` | Subagent type when `context: fork` |
| `hooks` | No | — | Skill lifecycle hooks |
| `paths` | No | — | Glob patterns limiting auto-activation |
| `shell` | No | `bash` | `bash` or `powershell` |

## String substitutions available in skill content

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed at invocation |
| `$ARGUMENTS[N]` | Nth argument (0-based) |
| `$N` | Shorthand for `$ARGUMENTS[N]` |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Directory containing this SKILL.md |

## Invocation control matrix

| Config | User can invoke | Claude can invoke |
|--------|----------------|-------------------|
| (default) | Yes | Yes |
| `disable-model-invocation: true` | Yes | No |
| `user-invocable: false` | No | Yes |

## Version note for marketplace plugins

For plugins referenced as relative paths in marketplace.json (e.g. `"source": "./plugins/my-plugin"`):
- Set version ONLY in `marketplace.json`, not in `plugin.json`
- If both are set, `plugin.json` silently overrides `marketplace.json`
