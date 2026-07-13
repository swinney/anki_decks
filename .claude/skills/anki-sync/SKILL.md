---
name: anki-sync
description: Safely reconcile hand-edited Anki cards with this repo's deck build scripts. Use whenever the user says they edited cards in Anki, asks to rebuild/update/import a deck, mentions losing cards or descriptions, or before ANY deck rebuild — a rebuild silently overwrites hand-edits. Also handles collection corruption recovery.
---

# anki-sync

Two-way sync between the deck builders in this repo and the live Anki collection.

## The problem

The user **hand-edits cards inside Anki while studying** (bold, bullet lists, pasted
AWS docs, sometimes retitling a card) and **also asks for programmatic deck
updates**. These fight:

- Decks use **stable per-service GUIDs**, so re-importing a rebuilt `.apkg` matches
  by GUID and **overwrites hand-edits with generated text**. This has caused real
  data loss more than once.
- Hand-edits exist **only in the collection** until something folds them into the
  build source. Any rebuild destroys them.

**Always audit before any rebuild or import — even if the user didn't say they'd
been editing. They often forget to mention it.**

## Commands

| Command | Writes to | Safe with Anki open? |
|---|---|---|
| `audit` (default) | nothing | **yes** — reads a copy |
| `pull` | build source only | **yes** — never touches the collection |
| `push` | the collection | **no** — guard refuses |
| `recover` | the collection (restore only) | **no** — guard refuses |

Interpreters are **not** interchangeable:

```bash
ENV_PY=/opt/homebrew/Caskroom/miniforge/base/envs/anki_decks/bin/python      # has genanki
ANKI_PY="$HOME/Library/Application Support/AnkiProgramFiles/.venv/bin/python" # has anki
S=.claude/skills/anki-sync/scripts

$ENV_PY  $S/audit.py                 # all decks; exit 1 if hand-edits are at risk
$ENV_PY  $S/audit.py aws             # one deck: aws | supplement | osi
$ENV_PY  $S/pull.py [--dry-run]      # fold hand-edits into the build, rebuild .apkg
$ANKI_PY $S/push.py [--dry-run]      # push build -> collection, surgically
$ENV_PY  $S/recover.py               # list + validate Anki's own backups
$ENV_PY  $S/recover.py --restore <backup-2026-...-.colpkg>
$ENV_PY  $S/recover.py --trace "X-Ray"   # when did this card's fields change?
```

`conda run -n anki_decks python3` resolves the **wrong** python (no genanki). Use the
path.

## Typical flows

**"I updated some cards"** → `audit` → `pull` → commit → (optionally) `push`.

**"Rebuild/update the deck"** → `audit` **first**. If it exits 1, `pull` and commit
before doing anything else, or you will destroy their work.

**"My cards are gone"** → `recover.py --trace <Service>` to find when it happened and
which version was theirs → `recover.py` to list candidates → restore.

## Non-negotiable rules

1. **`pgrep -x Anki` DOES NOT DETECT ANKI.** It runs as
   `.../AnkiProgramFiles/.venv/bin/python -c "import aqt; aqt.run()"`, so no
   name-based pgrep matches. That exact bug corrupted the collection (86 notes lost,
   broken index) by letting two processes write one SQLite file. Every write goes
   through `anki_guard.assert_anki_closed()`, which uses `lsof` on the collection
   plus an `aqt` command-line scan. Never trust a negative from a check you haven't
   seen return a positive — you can test the guard by launching Anki and confirming
   it aborts.
2. **Never fix collection fields by re-importing the `.apkg`.** That rewrites every
   note in the deck. `push.py` sets only the drifted fields on the drifted notes.
3. **Never write `notes.tags` / `notes.flds` with raw SQL.** It skips the tag
   registry and mishandles `usn`, which can force a destructive one-way AnkiWeb sync
   (the user syncs). Use the Collection API: `col.get_note` → `note.fields[i] = …` /
   `note.add_tag` → `col.update_notes`.
4. **Backup before every write; prove scheduling didn't move after.** `ivl/due/reps/
   lapses/queue/type` must be unchanged. Review history is the only thing that
   cannot be rebuilt from source.
5. **Report risk, not diffs.** "2 unprotected hand-edits, 30 bold runs, would be
   destroyed by the next rebuild" — not "2 fields differ".
6. **If the user pasted a wrong AWS fact, fix it and say so.** A study deck that is
   confidently wrong is worse than one that is silent.
7. After any collection write, tell them: **Tools → Check Database**, then sync — and
   if Anki demands a one-way sync, the answer is **Upload** (local is authoritative).

## How protection works

Hand-edits survive rebuilds only if they live in an override dict in the build source:

| Field | Protected by | Where |
|---|---|---|
| `Description` | `RICH_DESCRIPTIONS` | `AWS_certified_architect_associate/deck_versions/build_deck.py` |
| `Service` (card front) | `DISPLAY_NAMES` | `…/build_deck_v2.py` |

`DISPLAY_NAMES` overrides only the rendered field 0 — the service **name** stays the
key that joins `SERVICES` / `URL` / `EXAM` / `BEST_PRACTICES` and derives the GUID.

**Not protectable, and you must say so plainly when it comes up:**
- `Pick` / `Confuse` / `Scope` are **HTML-escaped** by the builder, so hand-added
  markup there cannot survive a rebuild.
- The **supplement** and **OSI** decks have **no override dicts at all**. `audit`
  reports hand-edits there; folding them in means editing the card literal by hand.

## Decks

| key | Deck in Anki | Builder | Notes | GUID |
|---|---|---|---|---|
| `aws` | `AWS::Services` | `AWS_certified_architect_associate/deck_versions/build_deck_v2.py` | 110 | `awscard-` + md5(name)[:12] |
| `supplement` | `AWS Interview Supplement — HBS Stack` | `aws_interview_supplement/deck_versions/build_deck.py` | 20 | `hbssupp-` + md5(key)[:12] |
| `osi` | `AWS::OSI Layers for AWS SAs` | `osi_layers_aws/deck_versions/build_deck.py` | 43 | `osicard-` + md5(key)[:12] |

Study session: `tag:stack::hbs` spans all three (68 cards). See "Focused study
sessions" in the AWS deck README.

## Implementation notes

- `audit` gets the expected notes by **running the real builder** with `genanki`
  monkeypatched (`add_note` records, `write_to_file` no-ops), so it never duplicates
  field-assembly logic and never writes a file. Each deck runs in its own subprocess
  — all three deck folders contain a module named `build_deck`, which collides in
  `sys.modules`.
- Anki normalises HTML entities on import (`'` ↔ `&#x27;`), so a raw byte diff is a
  false positive. `audit` compares **rendered** text and ignores cosmetic differences.
- Direction is decided by richness = `(count of <b>, visible length)`. Hand-edits add
  bold. When both sides are genuinely edited, **ask the user** — do not guess.
- Anki's `backups/*.colpkg` are written **by Anki**, so they are internally consistent
  — the most trustworthy recovery source. A file byte-copied from under a running
  Anki is not, even if it looks fine. Validate any candidate with `integrity_check`
  plus note/card/**revlog** counts before restoring, and preserve the bad file rather
  than deleting it.
