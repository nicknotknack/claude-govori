# govori: agent install guide

Claude Code plugin (macOS only): spoken replies via Piper (offline) with macOS `say` as fallback. Follow these steps to set it up on a fresh machine. Do them yourself, ask the user only where marked **ask**.

## 1. Check prerequisites

```bash
sw_vers -productName            # must be macOS
claude --version                # Claude Code CLI
command -v pipx brew            # pipx needed for Piper; brew install pipx if missing
```

## 2. Install the plugin

```bash
claude plugin marketplace add nicknotknack/claude-govori    # or a local clone path
claude plugin install govori@govori
```

Already installed? Run `claude plugin marketplace update govori && claude plugin update govori@govori`.

## 3. Install Piper (recommended; skip for `say` only)

```bash
pipx install piper-tts
piper --help | head -1            # verify
```

If pip fails with `ResolutionImpossible` (Python too new, e.g. 3.14+), use 3.13: `brew install python@3.13 && pipx install --python python3.13 piper-tts`.

## 4. Download voices (~60 MB each)

**ask** the user which languages they use. Defaults: Russian + English.

```bash
GOVORI=$(ls -d ~/.claude/plugins/cache/govori/govori/*/bin/govori | tail -1)
"$GOVORI" get ru_RU-denis-medium en_US-ryan-medium
"$GOVORI" voices                  # lists installed voices
```

`"$GOVORI" get` with no arguments lists all available voices. Names are `<lang>_<REGION>-<name>-<quality>`. Any language without an installed Piper voice falls back to `say`.

## 5. Verify

```bash
"$GOVORI" test "Готово. Проверяем git и Projects."
"$GOVORI" test "All done, tests are green."
```

The user should hear speech. If silent: run `piper --help` and `"$GOVORI" voices`, check system volume.

## 6. Optional config

Merge into `env` of `~/.claude/settings.json` (keep existing keys; back the file up first):

```json
"env": { "GOVORI_VOICES": "ru=denis,en=ryan", "GOVORI_RATE": "210" }
```

- `GOVORI_VOICES`: per language, part of a Piper voice name or a `say` voice name. Default: first installed.
- `GOVORI_RATE`: words per minute, default 210.

## 7. Finish

Tell the user: start a new Claude Code session, then type `/govori on` (`/govori off` to disable, `/govori` toggles). Nothing is added to context while it is off.

## Notes for contributors

- Code is one script, `bin/govori`; keep it small. State is the flag file `~/.claude/govori/on`; voices live in `~/.claude/govori/voices`.
- Test the Stop hook with `printf '%s' '{"last_assistant_message":"x\n\n🔊 Привет"}' | bin/govori hook-stop`. Use `printf`, not `echo`, in zsh.
- Installed plugins run from a cache copy, so bump `version` in `.claude-plugin/plugin.json` and run `claude plugin update govori@govori` after changes.
- Commits: Conventional Commits.
