#!/usr/bin/env python3
"""Push build -> collection for fields where the repo is authoritative.

Surgical: sets only the specific fields that drifted, on the specific notes that
drifted. This is deliberately NOT a re-import of the .apkg — an import rewrites
every note in the deck, including the HTML-escaped Pick/Confuse/Scope fields, and
would destroy any hand-edit there.

Refuses to run while Anki is open. Backs up first. Proves afterwards that no
card's scheduling moved — the review history is the one thing that cannot be
rebuilt from source.

Run with ANKI'S BUNDLED python (it has the `anki` package):
  ~/Library/Application\\ Support/AnkiProgramFiles/.venv/bin/python push.py [--dry-run]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ankilib as A                      # noqa: E402
from anki_guard import assert_anki_closed  # noqa: E402

DRY = "--dry-run" in sys.argv


def main():
    # Collect everything the repo is ahead on, before opening the collection.
    todo = []
    for key in A.DECKS:
        for x in A.audit(key):
            if x["kind"] == "build_richer":
                todo.append((key, x))

    if not todo:
        print("nothing to push — the collection matches the build everywhere")
        return

    print(f"{len(todo)} field(s) where the repo is ahead of the collection:\n")
    for key, x in todo:
        print(f"  [{x['label']}] {x['field']}: "
              f"{x['live_len']}ch -> {x['build_len']}ch")

    if DRY:
        print("\n--dry-run: nothing written")
        return

    assert_anki_closed(A.COL)
    A.backup()

    from anki.collection import Collection
    col = Collection(A.COL)
    before = A.sched_snapshot(col)

    notes, seen = [], {}
    for key, x in todo:
        fields = A.DECKS[key]["fields"]
        nids = col.db.list("SELECT id FROM notes WHERE guid=?", x["guid"])
        if len(nids) != 1:
            raise SystemExit(f"{x['label']}: expected 1 note, found {len(nids)}")
        note = seen.get(nids[0]) or col.get_note(nids[0])
        seen[nids[0]] = note
        note.fields[fields.index(x["field"])] = x["build"]

    notes = list(seen.values())
    col.update_notes(notes)
    print(f"\nupdated {len(notes)} note(s) — named fields only")

    A.assert_no_drift(before, A.sched_snapshot(col))
    col.close()

    print("\nre-auditing ...")
    left = sum(len(A.audit(k)) for k in A.DECKS)
    print(f"remaining drifts: {left}")
    print("\nOpen Anki -> Tools -> Check Database, then sync.")
    print("If Anki demands a one-way sync, choose UPLOAD: your local copy is authoritative.")


if __name__ == "__main__":
    main()
