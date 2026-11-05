# govori

Spoken replies for Claude Code on macOS. Claude ends each reply with a short `🔊` line, and [Piper](https://github.com/OHF-Voice/piper1-gpl), an offline neural TTS, reads it aloud. Off by default, zero context cost until you turn it on.

```bash
claude plugin marketplace add nicknotknack/claude-govori && claude plugin install govori@govori
```

Restart Claude Code and type `/govori`. It walks you through the rest and lets you hear each voice, pitch and speed before you keep it.

![govori](assets/cover.jpg)

## Commands

| Command | What it does |
|---|---|
| `/govori` | Turns voice on or off. The first time, runs the setup |
| `/govori settings` | Changes the voice, pitch and speed, and whether `/govori` applies to one session or all |
| `/govori on` / `off` / `status` | Sets voice on or off, or shows its state |
| `/govori test [text]` | Plays a sample |

## Good to know

- Replies in a language with no installed voice stay silent. Add languages in `/govori settings`.
- Ask Claude to "read this aloud" and it speaks that text instead of a summary.
- While in use, voices take about 150 MB of memory per language. The background process exits after 15 minutes of silence.

Setting up through an agent? Point it at [`AGENTS.md`](AGENTS.md).

## Uninstall

```bash
claude plugin uninstall govori@govori
rm -r ~/.claude/govori          # settings and voices
pipx uninstall piper-tts        # Piper
```
