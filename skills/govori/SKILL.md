---
name: govori
description: Toggle spoken replies (text-to-speech). Usage - /govori [on|off|status|voices|get|test]
argument-hint: "[on | off | status | voices | get <voice> | test [text]]"
disable-model-invocation: true
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/bin/govori" *)
---

Run `"${CLAUDE_PLUGIN_ROOT}/bin/govori" $ARGUMENTS` and follow its output exactly. Add nothing else; confirm in one short line.
