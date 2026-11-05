# govori

Spoken replies for Claude Code on macOS. Claude ends each reply with a short `🔊` line, and [Piper](https://github.com/OHF-Voice/piper1-gpl), an offline neural TTS, reads it aloud. Off by default, zero context cost until you turn it on. The name is Russian for "speak".

```bash
claude plugin marketplace add nicknotknack/claude-govori && claude plugin install govori@govori
```

Then restart Claude Code and type `/govori`. It asks a few questions, installs Piper (about 200 MB, needs Homebrew or pipx) and downloads the voices you pick (about 60 MB each).

![govori](assets/cover.jpg)

## Commands

| Command | What it does |
|---|---|
| `/govori` | Turns voice on or off. The first time, runs the setup |
| `/govori settings` | Changes the voice, pitch and speed, and whether `/govori` applies to one session or all |
| `/govori on` / `off` / `status` | Sets voice on or off, or shows its state |
| `/govori test [text]` | Plays a sample |

## Good to know

- Speaks any language Piper has a voice for. Replies in a language with no installed voice stay silent, so add the ones you use in `/govori settings`.
- Ask Claude to "read this aloud" and it speaks that text instead of a summary.
- While in use, voices take about 150 MB of memory per language. The background process exits after 15 minutes of silence.

Setting up through an agent? Point it at [`AGENTS.md`](AGENTS.md).

## Uninstall

```bash
claude plugin uninstall govori@govori
rm -r ~/.claude/govori          # settings and voices
pipx uninstall piper-tts        # Piper
```
