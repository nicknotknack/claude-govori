# govori

Spoken replies for Claude Code on macOS. Claude ends each reply with a short `🔊` line, and a TTS engine reads it aloud. Off by default, zero context cost until you turn it on.

```bash
claude plugin marketplace add nicknotknack/claude-govori && claude plugin install govori@govori
```

![govori](assets/cover.jpg)

Restart Claude Code, then type `/govori`.


## Better voices (optional)

The command above is enough: it works right away with `say`. For natural voices, add Piper:

```bash
pipx install piper-tts          # on a very new Python add: --python python3.13
```

Then download voices (~60 MB each). In Claude Code, or run `bin/govori get ...` from the plugin folder:

```
/govori get ru_RU-denis-medium en_US-ryan-medium
```

`/govori get` with no names lists every available voice. Voices live in `~/.claude/govori/voices`.

Setting up with an agent, or on another Mac: point Claude Code at [`AGENTS.md`](AGENTS.md), it has the exact steps.

## Use

| Command | Effect |
|---|---|
| `/govori` | Toggle on/off |
| `/govori on` / `off` / `status` | Set explicitly / show state |
| `/govori voices` | List installed Piper voices |
| `/govori get <voice>...` | Download Piper voices |
| `/govori test [text]` | Speak a sample, e.g. `/govori test Привет, git и Projects` |

- **On** applies at once, in the current session only (other and new sessions stay silent). **Off** removes the instruction and the speech. Type `/govori` again to switch it back.
- To make one switch control **every** session, opt in explicitly with `GOVORI_SCOPE=global` (see [Config](#config)).
- Ask Claude to "read this code aloud" and it puts that text in the voice block instead of a summary.

## Language

Each voice block's language is detected. Piper is used if a voice for that language is installed, else `say` with the best matching system voice.

- Russian with English words (`git`, `Projects`) stays Russian as long as at least a quarter of the words are Cyrillic. Piper's Russian voices pronounce Latin words with English sounds, with an accent.
- Plain ASCII text is treated as English without asking macOS. So German or Spanish written without any accented letters is read by the English voice.
- Anything else goes through macOS NaturalLanguage, which adds about 0.1 s.

## Config

All settings are optional environment variables. Put them in the `env` block of `~/.claude/settings.json`: Claude Code passes them to the plugin's hooks and commands. They apply to new sessions.

```json
{
  "env": {
    "GOVORI_COMMENT": "Settings of the govori plugin (spoken replies)",
    "GOVORI_VOICES": "ru=denis,en=ryan",
    "GOVORI_RATE": "210",
    "GOVORI_SCOPE": "session",
    "GOVORI_IDLE": "900"
  }
}
```

If the file already has an `env` block, add the lines to it instead of creating a second one.

| Var | Default | What it does |
|---|---|---|
| `GOVORI_VOICES` | first installed, alphabetically | Voice per language: part of a Piper voice name, or a `say` voice name. E.g. `ru=ruslan,en=Daniel` |
| `GOVORI_RATE` | `210` | Words per minute. Used directly by `say`; Piper's speed is scaled from it |
| `GOVORI_SCOPE` | unset (per session) | `global`: one switch for all sessions, current and new. Anything else keeps it per session |
| `GOVORI_IDLE` | `900` | Seconds without speech before the voice process exits and frees its memory |
| `GOVORI_COMMENT` | none | Ignored by the plugin. JSON has no comments, so this is one way to label the block |

- `export` in `~/.zshrc` also works, but only for Claude Code started from that terminal. `settings.json` is more reliable.
- `GOVORI_IDLE` is read when the voice process starts. If it is already running, the new value applies after `/govori off` and `/govori on`.
- Compare voices without changing settings, from the plugin folder: `GOVORI_VOICES=ru=ruslan bin/govori test "Готово, тесты зелёные"`.

## Speed and memory

While voice mode is on, Piper voices stay loaded in one background process, so speech starts without reloading a model. Measured on an M1 Pro, from the end of the reply to the start of playback:

| Case | Time |
|---|---|
| Piper, voice process running | 0.2–0.3 s |
| Piper, first reply with no voice process yet | about 1.4 s |
| `say` | about 0.15 s (about 1.6 s once, while the voice list is cached) |

- **Memory:** about 150 MB per language, one voice per installed language; about 280 MB for Russian and English. Almost no CPU while idle.
- **When it runs:** it starts on `/govori on`, or on the first spoken reply if the flag was already set. It never starts while voice mode is off. It exits on `/govori off` or after `GOVORI_IDLE` seconds without speech.

## Several sessions

Any number of sessions share one voice process, so nothing is duplicated: a second copy sees the lock and exits at once. No helper processes stay behind after a reply, and voices never overlap.

- A new reply from any session cuts off the one playing. If sessions finish almost together, you hear only the last one.
- `/govori off` in one session stops the voice process for all of them. Voice mode stays on in the others; their next reply restarts it and takes about 1.4 s. Speech already playing finishes.

## How it works

State is a flag file per session, `~/.claude/govori/sessions/<session id>` (stale ones are deleted after 14 days). With `GOVORI_SCOPE=global` it is the single file `~/.claude/govori/on` instead. `SessionStart` prints the rules when the flag exists; `Stop` takes everything from the last `🔊` line of `last_assistant_message`, detects its language and speaks it in the background. No marker, no speech.

Speech goes through `bin/govori-server.py` over the socket `~/.claude/govori/piper.sock`. If it can't answer, a one-shot `piper` takes over. `/govori test` uses it when it's running but never starts it. The `say` voice list is cached in `~/.claude/govori/say-voices` and refreshed on `/govori on`, so a newly installed system voice appears after that.

Uninstall: `claude plugin uninstall govori@govori`.
