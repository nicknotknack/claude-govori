# govori

Spoken replies for Claude Code on macOS. Claude ends each reply with a short `🔊` line, and a TTS engine reads it aloud. Off by default, zero context cost until you turn it on.

Engines: **[Piper](https://github.com/OHF-Voice/piper1-gpl)** (free, offline, natural voices) when a voice for the reply's language is installed, otherwise macOS `say`.

## Install

On another Mac, or with an agent: point Claude Code at [`AGENTS.md`](AGENTS.md), it has the exact steps.

```bash
claude plugin marketplace add nicknotknack/claude-govori
claude plugin install govori@govori
```

Works right away with `say`. For better voices, add Piper (optional):

```bash
pipx install piper-tts          # on a very new Python add: --python python3.13
```

Then download voices (~60 MB each). In Claude Code, or run `bin/govori get ...` from the plugin folder:

```
/govori get ru_RU-denis-medium en_US-ryan-medium
```

`/govori get` with no names lists every available voice. Voices live in `~/.claude/govori/voices`.

## Use

| Command | Effect |
|---|---|
| `/govori` | Toggle on/off |
| `/govori on` / `off` / `status` | Set explicitly / show state |
| `/govori voices` | List installed Piper voices |
| `/govori get <voice>...` | Download Piper voices |
| `/govori test [text]` | Speak a sample, e.g. `/govori test Привет, git и Projects` |

- **On** applies at once in the current session and in every new one. **Off** removes the instruction and the speech.
- Ask Claude to "read this code aloud" and it puts that text in the voice block instead of a summary.
- Each voice block's language is detected (macOS NaturalLanguage). Piper is used if a voice for that language is installed, else `say` with the best matching system voice.
- Mixed text (Russian with English words like `git`, `Projects`) is read by the voice of the main language. Piper's Russian voices pronounce Latin words with English sounds, with an accent.

## Config (optional env vars)

Set in `~/.claude/settings.json` under `env`, effective in new sessions.

| Var | Default | Example |
|---|---|---|
| `GOVORI_RATE` | `210` | words per minute (`say`); Piper speed is scaled from it |
| `GOVORI_VOICES` | first installed | `ru=ruslan,en=Daniel` per language: part of a Piper voice name, or a `say` voice name |

```json
"env": { "GOVORI_VOICES": "ru=ruslan", "GOVORI_RATE": "230" }
```

Compare voices: `GOVORI_VOICES=ru=ruslan bin/govori test "Готово, тесты зелёные"`.

## How it works

One flag file `~/.claude/govori/on`. `SessionStart` prints the rules when the flag exists; `Stop` takes everything from the last `🔊` line of `last_assistant_message`, detects its language and speaks it in the background. No marker, no speech. A new reply cuts off the previous one.

Uninstall: `claude plugin uninstall govori@govori`.
