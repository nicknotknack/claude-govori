---
name: govori
description: Toggle spoken replies (text-to-speech) for this session. Usage - /govori [on|off|status|voices|get|test]
argument-hint: "[on | off | status | voices | get <voice> | test [text]]"
disable-model-invocation: true
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/bin/govori" *)
---

Run `"${CLAUDE_PLUGIN_ROOT}/bin/govori" $ARGUMENTS` and follow its output exactly. Confirm in one short line, written once: while voice mode is on, that line is the 🔊 block itself, with no plain copy above it.
