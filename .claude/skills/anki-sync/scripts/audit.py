#!/usr/bin/env python3
"""READ-ONLY: diff every field of every note in all three decks against the builders.

Safe to run with Anki open — it reads a copy and writes nothing, anywhere.

Run with the CONDA env python:
  /opt/homebrew/Caskroom/miniforge/base/envs/anki_decks/bin/python audit.py [deck...]

Exit code 1 if anything unprotected is at risk, so it can gate a rebuild.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ankilib as A  # noqa: E402

keys = [k for k in sys.argv[1:] if k in A.DECKS] or list(A.DECKS)

at_risk, stale, total = [], [], 0
print("=" * 78)
for key in keys:
    d = A.DECKS[key]
    drifts = A.audit(key)
    total += len(drifts)
    print(f"\n### {d['name']}   ({len(drifts)} drift{'s' if len(drifts) != 1 else ''})")
    if not drifts:
        print("    in sync — every field matches the build")
        continue

    for x in drifts:
        if x["kind"] == "live_richer":
            # A hand-edit. Protected => foldable. Escaped => CANNOT be preserved.
            if x["escaped"]:
                tag = "HAND-EDIT, UNPROTECTABLE (field is HTML-escaped by the builder)"
            elif x["protected_by"]:
                tag = f"hand-edit -> foldable into {x['protected_by']}"
                at_risk.append((key, x))
            else:
                tag = "HAND-EDIT, NO OVERRIDE DICT for this field"
            print(f"    [{x['label']}] {x['field']}: "
                  f"live {x['live_len']}ch/{x['live_bold']}b vs build "
                  f"{x['build_len']}ch/{x['build_bold']}b  <- {tag}")
        elif x["kind"] == "build_richer":
            stale.append((key, x))
            print(f"    [{x['label']}] {x['field']}: "
                  f"live {x['live_len']}ch/{x['live_bold']}b vs build "
                  f"{x['build_len']}ch/{x['build_bold']}b  <- collection is STALE; "
                  f"build is authoritative")
        elif x["kind"] == "tags":
            print(f"    [{x['label']}] TAGS: live {x['live']!r} vs build {x['build']!r}")
        else:
            print(f"    [{x['label']}] {x['kind']}")

print("\n" + "=" * 78)
print("SUMMARY")
print(f"  hand-edits that a rebuild would DESTROY : {len(at_risk)}")
print(f"  fields where the collection is stale    : {len(stale)}")
print(f"  total drifts                            : {total}")

if at_risk:
    bolds = sum(x["live_bold"] for _, x in at_risk)
    print(f"\n  !! {len(at_risk)} unprotected hand-edit(s), {bolds} bold run(s) of your own")
    print("     work, would be silently overwritten by the next rebuild + import.")
    print("     Run:  /anki-sync pull    (folds them into the build source)")
if stale:
    print(f"\n  {len(stale)} field(s) where the repo is ahead of the collection.")
    print("     Run:  /anki-sync push    (surgical; never a re-import)")
if not total:
    print("\n  Nothing to do. Safe to rebuild.")

sys.exit(1 if at_risk else 0)
