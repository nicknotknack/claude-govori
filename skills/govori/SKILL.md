---
name: govori
description: Toggle spoken replies (text-to-speech) and change their settings. Usage - /govori [on|off|status|settings|voices|get|test]
argument-hint: "[on | off | status | settings | voices | get <voice> | test [text]]"
disable-model-invocation: true
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/bin/govori" *), Read, AskUserQuestion
---

Run `"${CLAUDE_PLUGIN_ROOT}/bin/govori" $ARGUMENTS`, then go by its output:

- Starts with `SETUP NEEDED`: read `${CLAUDE_SKILL_DIR}/setup.md` and follow "First run".
- Starts with `SETTINGS`: read `${CLAUDE_SKILL_DIR}/setup.md` and follow "Settings".
- Anything else: follow it exactly. Confirm in one short line, written once: while voice mode is on, that line is the 🔊 block itself, with no plain copy above it.

In `setup.md`, `govori` means `"${CLAUDE_PLUGIN_ROOT}/bin/govori"`.
