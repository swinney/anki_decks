#!/usr/bin/env python3
"""Emit, as JSON, exactly the notes a deck builder would produce — writing nothing.

Runs under the CONDA env python (the one with genanki), invoked as a subprocess by
ankilib.expected_notes(). One deck per process, because all three deck folders
contain a module literally named `build_deck` and importing two of them in one
interpreter collides in sys.modules.

Rather than re-implementing each builder's field assembly (which would silently
drift from the real thing), this runs the actual builder with genanki patched:
  - Deck.add_note        -> also records the Note
  - Package.write_to_file -> no-op, so no .apkg is written and the audit stays
                             genuinely read-only

usage: _extract.py <deck_dir> <builder_path>
"""
import io
import sys
import json
import runpy
import contextlib

deck_dir, builder = sys.argv[1], sys.argv[2]
sys.path.insert(0, deck_dir)

import genanki  # noqa: E402

notes = []
_orig_add = genanki.Deck.add_note


def _add_note(self, note):
    notes.append(note)
    return _orig_add(self, note)


genanki.Deck.add_note = _add_note
genanki.Package.write_to_file = lambda self, *a, **k: None   # write nothing

# Builders print "Wrote N cards"; keep stdout clean for the JSON payload.
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    runpy.run_path(builder, run_name="__main__")

print(json.dumps({
    n.guid: {"fields": list(n.fields), "tags": sorted(n.tags)}
    for n in notes
}))
