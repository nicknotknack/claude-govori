# govori: agent install guide

Claude Code plugin (macOS only): spoken replies via Piper (offline neural TTS). Do these steps yourself on the user's machine.

## Install

```bash
sw_vers -productName    # must be macOS; stop and tell the user if it is not
claude plugin marketplace add nicknotknack/claude-govori && claude plugin install govori@govori    # or a local clone path instead of owner/repo
```

Already installed? Run `claude plugin marketplace update govori && claude plugin update govori@govori`.

Then tell the user: restart Claude Code and type `/govori`. That is the whole install.

Do not install Piper, download voices or write settings yourself. The first `/govori` does all of that with the user in dialogs: Piper, scope, languages and voices, speed. Its steps are in `skills/govori/setup.md`.

If the machine has `GOVORI_*` keys in `env` of `~/.claude/settings.json`, from an older version, remove them: they are no longer read. Keep every other key.

## If something fails

- `/govori` is an unknown command: Claude Code was not restarted, or the plugin is disabled.
- `install-piper` fails with `pipx is required`: install Homebrew or pipx, then run `/govori` again.
- No sound: run `/govori voices` and `/govori test`, check the system volume. A language with no installed voice stays silent.

## Notes for contributors

- Code is `bin/govori` plus the voice server `bin/govori-server.py`; keep both small. Dialogs live in `skills/govori/setup.md`, which only the skill reads. The server must only ever be started while voice mode is on (`on`, or a Stop hook whose session has the flag). State is a flag file per session, `~/.claude/govori/sessions/<session id>`, or the single file `~/.claude/govori/on` with `scope=global`. Settings are in `~/.claude/govori/config`, voices in `~/.claude/govori/voices`. Hooks read `session_id` from stdin JSON, commands from `$CLAUDE_CODE_SESSION_ID`.
- Test the Stop hook: first `CLAUDE_CODE_SESSION_ID=s1 bin/govori setup-done` (`on` only asks for setup until then), then `printf '%s' '{"session_id":"s1","last_assistant_message":"x\n\n🔊 Привет"}' | bin/govori hook-stop`. Use `printf`, not `echo`, in zsh. Use a throwaway `HOME` so tests don't touch real state (symlink each file of `~/.claude/govori/voices` into its own `voices` folder, so `remove` can't reach the real ones, and put the real `~/.local/bin` on `PATH`).
- Tests must stay silent and must not touch the real server: put a stub `afplay` first on `PATH` that logs and runs `exec /usr/bin/afplay -v 0 "$1"`. A real process named `afplay` is what `pkill -x afplay` matches, so overlap counts stay honest. Check processes with `pgrep -f "govori-server.py $HOME"`.
- Dialogs can't be tested from a script: after changing `setup.md`, delete the config in a real session and go through `/govori` by hand.
- Installed plugins run from a cache copy, so bump `version` in `.claude-plugin/plugin.json` and run `claude plugin marketplace update govori && claude plugin update govori@govori` after changes, then restart Claude Code. The maintainer's marketplace source is the local folder, so this needs no push.
- Commits: Conventional Commits.

## Design notes

Latency, measured on an M1 Pro: a fresh `piper` needs about 1.4 s whatever the text length, nearly all of it loading the ~60 MB ONNX model (`import` is 0.1 s, synthesis of two sentences 0.17 s). `osascript` takes 0.1 s, `plutil` 0.05 s. Keep them off the speech path where possible.

Decisions worth keeping, and why:

- **Server starts only while voice mode is on** (explicit user requirement). `on` starts it; `speak` starts it lazily, which covers resumed sessions. `hook-start` and `test` must not. `VOICE_ON` carries this into `piper_talk`.
- **One server for all sessions.** `flock` on `piper.lock` is taken before importing Piper, so a redundant copy exits cheaply. Verified with 5 sessions starting and speaking at once: 1 server, 1 `afplay`, no leftovers.
- **Requests beat preloading.** Voices load one at a time between non-blocking `accept` calls, and `server_start` puts the voice it needs first, so a waiting reply is delayed by at most one load. The socket is bound before loading, so early requests queue instead of loading a second copy.
- **Socket path is relative** (`cd "$D"`): `sun_path` is limited to 104 bytes, which a long `HOME` exceeds. Requests are NUL-terminated because bash strings can't contain NUL. The answer is `ok` or `err`; only an empty answer means "not running" and retries, `err` goes straight to the one-shot `piper`.
- **Language detection** works on bytes in `LC_ALL=C` and counts words, not letters: macOS NaturalLanguage called "Готово, git и Projects" English. Threshold is 25% Cyrillic words. Restore the locale before `osascript`. The accepted trade-off: ASCII-only German or Spanish is read as English.
- **`session_id` comes from a regex on the raw JSON**, not `plutil`: quotes are escaped inside JSON strings, so a message can't fake a match. A voice-off session pays for no `plutil` at all.
- **`/bin/bash` on macOS is 3.2:** no associative arrays or `${x,,}`.
- **Settings live in `config`, not `settings.json`,** so the plugin adds nothing to Claude Code's own config, and voice and speed apply from the next reply. It is parsed with `read`, never sourced: no extra process on the speech path, and the file can't run code.
- **The script owns the rules, the skill owns the dialog.** Claude only calls `govori set`, which validates, and never edits the file. `setup=done` is written last, by `setup-done`, so a cancelled setup leaves voice off and the next `/govori` resumes it.
- **`set scope` keeps the current session's state:** it clears the old flag and sets the new one, so switching never turns voice on for someone who had it off.
- **Speed and pitch are tuned by ear in one click.** Every value plays, then one dialog offers keep, lower or higher, with no "Change" step in between. The lists of values are in `setup.md`.
- **Piper's speed is not linear.** Measured: length scale 0.5 shortens a clip by about a third, not by half, and the same text varies by a few percent between runs. Don't compare clip lengths exactly in tests.
- **Pitch is a changed WAV sample rate,** written by `retune` in the server, with the length scale multiplied by the pitch so the duration stays about the same. It needs no new dependency and adds no measurable delay, and it also shifts formants, which is what makes a voice sound deeper. Far from 1 it sounds artificial, hence the 0.7 to 1.3 limit.
- **Piper is the only engine.** `say` was removed to keep one code path. `on` refuses without Piper or a voice, because otherwise Claude would add `🔊` lines that nobody hears.

Known limits and open ideas:

- macOS only: besides bash, the code needs `afplay`, `osascript`, `plutil`, `nc -U`, `pkill`, and the server uses `fcntl` and Unix sockets. A Windows port means replacing all of these.
- New speech cuts off the current one across all sessions, so near-simultaneous replies are lost except the last. A queue would keep them all, at the cost of a long reply delaying the next. Not built; the behaviour matches earlier versions.
- `/govori off` stops the server for every session; the others restart it on their next reply.
- With `scope=global`, sessions already open get the rules only after a restart, because `SessionStart` delivers them. A `UserPromptSubmit` hook would fix that at the cost of context on every message. Not built.
- Speech starts after the whole text is synthesized. Sentence-by-sentence playback would only help long dictation, since two sentences take about 0.17 s.
