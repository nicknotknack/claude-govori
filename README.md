# govori

Spoken replies for Claude Code on macOS. Claude ends each reply with a short `🔊` line, and [Piper](https://github.com/OHF-Voice/piper1-gpl), an offline neural TTS, reads it aloud. Off by default, zero context cost until you turn it on.

![govori](assets/cover.jpg)

## Install

```bash
claude plugin marketplace add nicknotknack/claude-govori && claude plugin install govori@govori
```

Restart Claude Code and type `/govori`. The first run sets everything up in dialogs right in the session:

1. Installs Piper if it is missing, after asking.
2. Asks whether to speak in this session only or in all sessions.
3. Asks your languages, then a voice for each. It downloads the voice (~60 MB) and plays a sample, so you can keep it or try another.
4. Asks the pitch and the speech speed. Each value plays at once, and you keep it or try a step lower or higher.

Voice mode turns on when you finish. If you cancel, nothing is turned on, and the next `/govori` picks up setup again.

Setting up with an agent, or on another Mac: point Claude Code at [`AGENTS.md`](AGENTS.md).

## Use

| Command | Effect |
|---|---|
| `/govori` | First time: setup. Then: toggle on/off |
| `/govori settings` | Change scope, voices, pitch and speed in a dialog, hearing each change |
| `/govori on` / `off` / `status` | Set explicitly / show state |
| `/govori voices` | List installed voices |
| `/govori get <voice>...` | Download voices. With no names, lists all available |
| `/govori test [text]` | Speak a sample, e.g. `/govori test Привет, git и Projects` |

- **This session scope:** on and off apply at once, to the current session only. Other and new sessions stay silent.
- **All sessions scope:** one switch for every session, and `/govori off` silences all of them. New sessions follow the switch. Sessions already open get the `🔊` rules only after a restart, because the rules are added at session start.
- Ask Claude to "read this code aloud" and it puts that text in the voice block instead of a summary.

## Language

Each voice block's language is detected and read by a Piper voice for that language. If none is installed, the reply stays silent, so install a voice for every language you use.

- Russian with English words (`git`, `Projects`) stays Russian as long as at least a quarter of the words are Cyrillic. Piper's Russian voices pronounce Latin words with English sounds, with an accent.
- Plain ASCII text is treated as English without asking macOS. So German or Spanish written without any accented letters is read by the English voice.
- Anything else goes through macOS NaturalLanguage, which adds about 0.1 s.

## Settings

Use `/govori settings`. Voice, pitch and speed apply from the next reply, no restart needed. Nothing goes into Claude Code's `settings.json`: the values live in `~/.claude/govori/config`, and voices in `~/.claude/govori/voices`.

```
scope=session
speed=1.17
pitch=1
voices=ru=dmitri,en=ryan
setup=done
```

| Key | Values |
|---|---|
| `scope` | `session` or `global` (all sessions) |
| `speed` | `0.5` to `3`. `1` is the voice's natural speed, higher is faster. Piper's speed is not linear: `2` shortens speech by about a third |
| `pitch` | `0.7` to `1.3`. `1` is the voice's own pitch, lower sounds deeper. The speed stays about the same |
| `voices` | Voice per language: part of a voice name. If nothing matches, the first installed voice of that language is used |
| `setup` | `done` once the first run has finished. Delete the file to run setup again |

Upgrading from an older version: the `GOVORI_*` variables are no longer read, so remove them from `env` in `~/.claude/settings.json`.

## Speed and memory

While voice mode is on, Piper voices stay loaded in one background process, so speech starts without reloading a model. Measured on an M1 Pro, from the end of the reply to the start of playback:

| Case | Time |
|---|---|
| Voice process running | 0.2–0.3 s |
| First reply with no voice process yet | about 1.4 s |

- **Memory:** about 150 MB per language, one voice per installed language; about 280 MB for Russian and English. Almost no CPU while idle.
- **When it runs:** it starts on `/govori on`, or on the first spoken reply if the flag was already set. It never starts while voice mode is off. It exits on `/govori off` or after 15 minutes without speech.

## Several sessions

Any number of sessions share one voice process, so nothing is duplicated: a second copy sees the lock and exits at once. No helper processes stay behind after a reply, and voices never overlap.

- A new reply from any session cuts off the one playing. If sessions finish almost together, you hear only the last one.
- `/govori off` in one session stops the voice process for all of them. In the this-session scope, voice mode stays on in the others; their next reply restarts it and takes about 1.4 s. Speech already playing finishes.

## How it works

State is a flag file per session, `~/.claude/govori/sessions/<session id>` (stale ones are deleted after 14 days), or the single file `~/.claude/govori/on` in the all-sessions scope. `SessionStart` prints the rules when the flag exists; `Stop` takes everything from the last `🔊` line of `last_assistant_message`, detects its language and speaks it in the background. No marker, no speech.

Speech goes through `bin/govori-server.py` over the socket `~/.claude/govori/piper.sock`. If it can't answer, a one-shot `piper` takes over. `/govori test` uses it when it's running but never starts it.

Uninstall: `claude plugin uninstall govori@govori`. To also remove settings and voices: `rm -r ~/.claude/govori`, and `pipx uninstall piper-tts` for Piper.
