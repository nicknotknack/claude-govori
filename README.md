# govori

Spoken replies for Claude Code on macOS. Claude ends each reply with a short `🔊` line, and [Piper](https://github.com/OHF-Voice/piper1-gpl), an offline neural TTS, reads it aloud. Off by default, zero context cost until you turn it on.

![govori](assets/cover.jpg)

## Install

Install the plugin and Piper:

```bash
claude plugin marketplace add nicknotknack/claude-govori && claude plugin install govori@govori
pipx install piper-tts          # on a very new Python add: --python python3.13
```

Restart Claude Code, download voices (~60 MB each), and turn it on:

```
/govori get ru_RU-denis-medium en_US-ryan-medium
/govori
```

`/govori get` with no names lists every available voice. Voices live in `~/.claude/govori/voices`. Without Piper or a voice, `/govori on` refuses and prints what to install.

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
- Ask Claude to "read this code aloud" and it puts that text in the voice block instead of a summary.

## Language

Each voice block's language is detected and read by a Piper voice for that language. If none is installed, the reply stays silent, so install a voice for every language you use.

- Russian with English words (`git`, `Projects`) stays Russian as long as at least a quarter of the words are Cyrillic. Piper's Russian voices pronounce Latin words with English sounds, with an accent.
- Plain ASCII text is treated as English without asking macOS. So German or Spanish written without any accented letters is read by the English voice.
- Anything else goes through macOS NaturalLanguage, which adds about 0.1 s.

## Config

All settings are optional environment variables. Put them in the `env` block of `~/.claude/settings.json`: Claude Code passes them to the plugin's hooks and commands. They apply to new sessions.

```json
{
  "env": {
    "GOVORI_VOICES": "ru=denis,en=ryan",
    "GOVORI_SPEED": "1.17"
  }
}
```

If the file already has an `env` block, add the lines to it instead of creating a second one.

| Var | Default | What it does |
|---|---|---|
| `GOVORI_VOICES` | first installed, alphabetically | Voice per language: part of a Piper voice name, e.g. `ru=ruslan,en=ryan`. If nothing matches, the first installed voice of that language is used |
| `GOVORI_SPEED` | `1.17` | Speech speed, a positive number: `1` is the voice's natural speed, `2` is twice as fast |

- `export` in `~/.zshrc` also works, but only for Claude Code started from that terminal. `settings.json` is more reliable.
- Compare voices without changing settings, from the plugin folder: `GOVORI_VOICES=ru=ruslan bin/govori test "Готово, тесты зелёные"`.

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
- `/govori off` in one session stops the voice process for all of them. Voice mode stays on in the others; their next reply restarts it and takes about 1.4 s. Speech already playing finishes.

## How it works

State is a flag file per session, `~/.claude/govori/sessions/<session id>` (stale ones are deleted after 14 days). `SessionStart` prints the rules when the flag exists; `Stop` takes everything from the last `🔊` line of `last_assistant_message`, detects its language and speaks it in the background. No marker, no speech.

Speech goes through `bin/govori-server.py` over the socket `~/.claude/govori/piper.sock`. If it can't answer, a one-shot `piper` takes over. `/govori test` uses it when it's running but never starts it.

Uninstall: `claude plugin uninstall govori@govori`.
