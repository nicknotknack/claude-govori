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
claude plugin marketplace add nicknotknack/claude-govori && claude plugin install govori@govori    # or a local clone path instead of owner/repo
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
"env": {
  "GOVORI_COMMENT": "Settings of the govori plugin (spoken replies)",
  "GOVORI_VOICES": "ru=denis,en=ryan",
  "GOVORI_RATE": "210",
  "GOVORI_SCOPE": "session",
  "GOVORI_IDLE": "900"
}
```

- `GOVORI_VOICES`: per language, part of a Piper voice name or a `say` voice name. Default: first installed, alphabetically.
- `GOVORI_RATE`: words per minute, default 210.
- `GOVORI_SCOPE`: `global` makes one switch for all sessions. Anything else, or unset, is per session.
- `GOVORI_IDLE`: seconds without speech before the voice process exits, default 900. Read when that process starts.
- `GOVORI_COMMENT`: ignored by the plugin. `settings.json` is plain JSON with no comments, so this labels the block.

Values apply to new sessions only.

## 7. Finish

Tell the user: start a new Claude Code session, then type `/govori` (toggles; `on` / `off` set it explicitly). It applies to that session only. Nothing is added to context while it is off. Only if the user wants one switch for all sessions, add `"GOVORI_SCOPE": "global"` to `env`.

## Notes for contributors

- Code is `bin/govori` plus the voice server `bin/govori-server.py`; keep both small. The server must only ever be started while voice mode is on (`on`, or a Stop hook whose session has the flag). State is a flag file per session, `~/.claude/govori/sessions/<session id>` (the single file `~/.claude/govori/on` when `GOVORI_SCOPE=global`); voices live in `~/.claude/govori/voices`. Hooks read `session_id` from stdin JSON, commands from `$CLAUDE_CODE_SESSION_ID`.
- Test the Stop hook: first `CLAUDE_CODE_SESSION_ID=s1 bin/govori on`, then `printf '%s' '{"session_id":"s1","last_assistant_message":"x\n\n🔊 Привет"}' | bin/govori hook-stop`. Use `printf`, not `echo`, in zsh. Use a throwaway `HOME` so tests don't touch real state (symlink `~/.claude/govori/voices` into it, and put the real `~/.local/bin` on `PATH`).
- Tests must stay silent and must not touch the real server: put a stub `afplay` first on `PATH` that logs and runs `exec /usr/bin/afplay -v 0 "$1"`. A real process named `afplay` is what `pkill -x afplay` matches, so overlap counts stay honest. Check processes with `pgrep -f "govori-server.py $HOME"`.
- Installed plugins run from a cache copy, so bump `version` in `.claude-plugin/plugin.json` and run `claude plugin marketplace update govori && claude plugin update govori@govori` after changes, then restart Claude Code. The maintainer's marketplace source is the local folder, so this needs no push.
- Commits: Conventional Commits.

## Design notes

Latency, measured on an M1 Pro: a fresh `piper` needs about 1.4 s whatever the text length, nearly all of it loading the ~60 MB ONNX model (`import` is 0.1 s, synthesis of two sentences 0.17 s). `say -v '?'` takes about 1.4 s, `osascript` 0.1 s, `plutil` 0.05 s. Keep all of them off the speech path.

Decisions worth keeping, and why:

- **Server starts only while voice mode is on** (explicit user requirement). `on` starts it; `speak` starts it lazily, which covers resumed sessions and global scope. `hook-start` and `test` must not. `VOICE_ON` carries this into `piper_talk`.
- **One server for all sessions.** `flock` on `piper.lock` is taken before importing Piper, so a redundant copy exits cheaply. Verified with 5 sessions starting and speaking at once: 1 server, 1 `afplay`, no leftovers.
- **Requests beat preloading.** Voices load one at a time between non-blocking `accept` calls, and `server_start` puts the voice it needs first, so a waiting reply is delayed by at most one load. The socket is bound before loading, so early requests queue instead of loading a second copy.
- **Socket path is relative** (`cd "$D"`): `sun_path` is limited to 104 bytes, which a long `HOME` exceeds. Requests are NUL-terminated because bash strings can't contain NUL. The answer is `ok` or `err`; only an empty answer means "not running" and retries, `err` goes straight to the one-shot `piper`.
- **Language detection** works on bytes in `LC_ALL=C` and counts words, not letters: macOS NaturalLanguage called "Готово, git и Projects" English. Threshold is 25% Cyrillic words. Restore the locale before `osascript`. The accepted trade-off: ASCII-only German or Spanish is read as English.
- **`session_id` comes from a regex on the raw JSON**, not `plutil`: quotes are escaped inside JSON strings, so a message can't fake a match. A voice-off session pays for no `plutil` at all.
- **`/bin/bash` on macOS is 3.2:** no associative arrays or `${x,,}`.

Known limits and open ideas:

- New speech cuts off the current one across all sessions, so near-simultaneous replies are lost except the last. A queue would keep them all, at the cost of a long reply delaying the next. Not built; the behaviour matches earlier versions.
- `/govori off` stops the server for every session; the others restart it on their next reply.
- Speech starts after the whole text is synthesized. Sentence-by-sentence playback would only help long dictation, since two sentences take about 0.17 s.
