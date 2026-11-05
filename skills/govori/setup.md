# govori setup and settings

Rules for both flows:

- Write to the user in their language. Keep every message to a line or two.
- Ask every choice with `AskUserQuestion`, never as plain text. It allows at most 4 questions per call and 4 options per question, and adds "Other" by itself.
- Change settings only through `govori set`. Never edit the config file.
- Run `govori install-piper` and `govori get` with a 10-minute Bash timeout: they download a lot.
- A test sample must be in the voice's language. For languages other than English and Russian it must contain accented letters, otherwise it is detected as English.

## Scope question

Used by both flows. The choice is lasting: it sets what every future `/govori` does, not what happens now. Translate this wording, keeping that meaning:

- Question: "What should /govori do each time you type it?"
- "This session only": "Each /govori turns voice on or off only in the session where you typed it."
- "All sessions": "Each /govori turns voice on or off in all sessions at once. Sessions already open start speaking after a restart."

Run `govori set scope session` or `govori set scope global`.

## Extra voices

Used by both flows, after voices are chosen. Run `govori extra`, which lists installed voices that are not the chosen one for their language. If it prints nothing, skip this.

Otherwise ask whether to delete them, naming each and saying each takes about 60 MB: "Delete (Recommended)" or "Keep". A voice of a language not chosen is on the list too, so say that replies in that language will go silent. On "Delete", run `govori remove <voice>...`. "Keep" or a dismissed dialog just moves on, and does not stop setup.

## Tuning speed or pitch

Used by both flows, so the user hears every value and adjusts it in one click:

1. Run `govori set <speed|pitch> <value>` and `govori test "<a short sentence>"`.
2. Without any other question in between, ask with exactly these options: "Keep <value>", "Try <lower>" and "Try <higher>", marked slower and faster for speed, lower and higher for pitch. "Other" takes any number in range.
3. On "Keep", stop. Otherwise go back to step 1 with the new value.

Take `<lower>` and `<higher>` from these lists: the nearest values at least 0.05 away from the current one. At the end of a list, leave that option out.

- Speed, range 0.5 to 3: 0.5, 0.8, 1, 1.1, 1.2, 1.4, 1.6, 2, 2.5, 3. For example, after 1.22 offer 1.1 and 1.4.
- Pitch, range 0.7 to 1.3: 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1, 1.05, 1.1, 1.2, 1.3. For example, after 0.92 offer 0.85 and 1.

## First run

The `SETUP NEEDED` line says whether Piper is installed and which voices already are. If the user declines or dismisses a dialog, stop: say voice stays off and that `/govori` resumes setup. Do not run `setup-done`.

1. **Piper** (only if missing). Ask whether to install it, offline speech engine, about 200 MB. On yes, run `govori install-piper`. If it fails, show the error and stop.
2. **Scope.** Ask the scope question, with "This session only" marked (Recommended).
3. **Languages.** Ask with `multiSelect: true`: the language of this conversation first, then others from Russian, English, German, Spanish. Map answers to two-letter codes (`ru`, `en`, `de`, `es`).
4. **Voice**, for each language, one at a time:
   1. Ask which voice, up to 4 options in this order, marking installed ones:
      - `ru`: `ru_RU-dmitri-medium` (male, Recommended), `ru_RU-denis-medium` (male), `ru_RU-irina-medium` (female), `ru_RU-ruslan-medium` (male)
      - `en`: `en_US-ryan-medium` (male), `en_US-amy-medium` (female), `en_US-lessac-medium` (female), `en_US-joe-medium` (male)
      - Otherwise run `govori catalog <code>` and offer up to 4, preferring `-medium`. If it prints nothing, say there is no voice for that language and skip it.
   2. Say it downloads about 60 MB unless installed, then run `govori get <voice>`, `govori set voice <code> <voice>` and `govori test "<a short sentence in that language>"`.
   3. Ask "Keep this voice?" with "Keep" and "Try another". On "Try another", run `govori remove <voice>` if this flow downloaded it, then go back to the voice question.
5. **Extra voices.** Offer to delete them (see "Extra voices").
6. **Pitch.** Ask: "1: natural (Recommended)", "0.9: lower", "0.8: much lower". Other accepts 0.7 to 1.3. Then tune it (see "Tuning speed or pitch").
7. **Speed.** Ask: "1.17: slightly fast (Recommended)", "1: natural", "1.4: fast". Other accepts 0.5 to 3. Then tune it the same way.
8. **Finish.** Run `govori setup-done` and follow its output. Confirm in one line that it works and that `/govori settings` changes everything later. With scope `global`, add that sessions already open need a restart.

## Settings

The `SETTINGS` output shows the current values. Ask everything in one `AskUserQuestion` call, each question with the current value as the first option, marked current:

- **Scope:** the scope question.
- **Speed:** 1, 1.17 and 1.4. Other accepts 0.5 to 3.
- **Pitch:** 1, 0.9 and 0.8. Other accepts 0.7 to 1.3.
- **Voice**, one question per language in `voices`: installed voices of that language, then "Another voice". If there is more than one language, ask the rest in a second call.

If the user dismisses the dialog, change nothing. Otherwise apply only what changed:

- Scope: `govori set scope <session|global>`.
- Speed or pitch: tune it (see "Tuning speed or pitch"), one at a time.
- Voice: `govori set voice <code> <voice>`, then `govori test` in that language. For "Another voice", follow step 4 of "First run". The same step adds a new language if the user asks for one in "Other". After any voice change, offer to delete extra voices (see "Extra voices").

Then confirm in one line what changed: voice, pitch and speed apply from the next reply. A scope change takes effect in sessions already open only after they restart.
