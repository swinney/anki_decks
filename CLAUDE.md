# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A collection of [Anki](https://apps.ankiweb.net/) flashcard decks, generated
programmatically with [genanki](https://github.com/kerrickstaley/genanki).
Each deck lives in its own subdirectory.

## Current decks

- `AWS_certified_architect_associate/` — AWS Certified Solutions Architect
  Associate (SAA-C03) study deck: 109 services with descriptions, linked
  homepages, associated services, and exam fields (Pick this when / Don't
  confuse with / Resilience scope). Has its own `README.md` and a companion
  `studyguide.md` for deeper topics beyond the deck.

## Environment

A single conda env named `anki_decks` covers the whole repo, defined at the
root `environment.yml` (Python 3.11 + genanki):

```bash
conda env create -f environment.yml   # first time only
conda activate anki_decks
```

## Building decks

Build scripts live in each deck's `deck_versions/` folder. For the AWS deck:

```bash
conda activate anki_decks
cd AWS_certified_architect_associate/deck_versions
python3 build_deck_v2.py   # writes ../AWS_Services.apkg
```

`build_deck_v2.py` imports service data from `build_deck.py` and the exam
fields from `exam_fields.py`. The latest `.apkg` lives at the deck root; prior
versions are kept in `deck_versions/`.

## How a card is assembled (AWS deck)

A single service's data is spread across four structures, joined by the
**service name as the key**:

- `build_deck.py` → `SERVICES` (list of `(name, category, description, assoc)`
  tuples), `URL` (name → AWS homepage), and `assoc_html()` (renders the
  associated-services links).
- `exam_fields.py` → `EXAM` (name → `(pick_when, dont_confuse_with,
  resilience_scope)`).
- `best_practices.py` → `BEST_PRACTICES` (name → AWS best-practices URL).
- `build_deck_v2.py` joins them: for each `SERVICES` entry it looks up `URL`,
  `EXAM`, and `BEST_PRACTICES` by name and emits a 9-field note.

**Adding/editing a service means touching all four keyed by the same exact
name.** `build_deck_v2.py` validates this up front — it raises `SystemExit` if
any service is missing a `URL`, `EXAM`, or `BEST_PRACTICES` entry — so a build
failure usually means a name mismatch or a forgotten entry, not a code bug.

## Conventions

- **Stable card IDs.** Every note's GUID is derived deterministically from the
  service name, so re-importing an updated deck *updates* existing cards in
  Anki instead of creating duplicates — preserving review history. Never switch
  to random GUIDs.
- **Keep the model id stable to evolve a deployed note type.** To add/remove a
  field (or change templates/CSS) *and* update cards people already studied,
  **keep the same `genanki.Model` id** and add new fields **at the end** — on
  re-import Anki matches notes by GUID, updates the note type in place, and
  preserves review history. Using a *new* model id makes Anki **reject** notes
  whose GUIDs already exist under the old type ("note type has changed"), so only
  mint a new id for a genuinely separate note type.
- **Edit data, not the .apkg.** Change `build_deck.py` / `exam_fields.py`, then
  rebuild. The `.apkg` is a generated artifact.
- **Verify before delivering.** After building, unzip the `.apkg` and check the
  notes table (count, field completeness, valid links) before sharing.

## Git workflow

- Commit finished work **directly to `main`** — no feature branches.
- Commit as soon as a deliverable is done.
- **Pushing happens from the user's Mac**, not from the Cowork sandbox (no
  GitHub network route or SSH keys here). After committing, remind the user to
  run `git push` from `~/Projects/anki_decks`.
- Remote: `git@github.com:swinney/anki_decks.git`.
