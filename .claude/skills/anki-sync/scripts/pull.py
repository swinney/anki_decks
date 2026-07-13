#!/usr/bin/env python3
"""Fold hand-edits made in Anki back into the build source, so rebuilds stop eating them.

Writes to build_deck.py (RICH_DESCRIPTIONS) and build_deck_v2.py (DISPLAY_NAMES),
verbatim — your text is your text. Then rebuilds the .apkg.

Touches the COLLECTION not at all, so it is safe with Anki open.

Only the AWS deck has override dicts. A hand-edit in the supplement or OSI deck,
or in an HTML-escaped field (Pick/Confuse/Scope), CANNOT be protected this way —
those are reported and left for you to decide.

Run with the CONDA env python:
  .../envs/anki_decks/bin/python pull.py [--dry-run]
"""
import os
import re
import sys
import ast
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ankilib as A  # noqa: E402

DRY = "--dry-run" in sys.argv

AWS = A.DECKS["aws"]
BD = os.path.join(AWS["dir"], "build_deck.py")
BD2 = os.path.join(AWS["dir"], "build_deck_v2.py")

# (dict name, file, the text that terminates the literal in that file)
BLOCKS = {
    "RICH_DESCRIPTIONS": (BD, "}\n\n# Apply the recovered descriptions over the plain fallbacks defined above."),
    "DISPLAY_NAMES": (BD2, "}\nunknown_display = set(DISPLAY_NAMES) - service_names"),
}


def load_dict(name):
    path, end_marker = BLOCKS[name]
    src = open(path).read()
    start = src.index(f"{name} = {{")
    end = src.index(end_marker, start)
    return ast.literal_eval(src[src.index("{", start):end + 1])


def write_dict(name, data):
    path, end_marker = BLOCKS[name]
    src = open(path).read()
    start = src.index(f"{name} = {{")
    end = src.index(end_marker, start)
    block = f"{name} = {{\n" + "".join(f"    {k!r}: {data[k]!r},\n" for k in sorted(data))
    new = src[:start] + block + src[end:]
    ast.parse(new)                       # syntax gate before touching the file
    if not DRY:
        open(path, "w").write(new)
    return os.path.basename(path)


def main():
    sys.path.insert(0, AWS["dir"])
    from build_deck import SERVICES
    by_guid = {A.aws_guid(n): n for n, *_ in SERVICES}

    updates = {"RICH_DESCRIPTIONS": {}, "DISPLAY_NAMES": {}}
    unprotectable = []

    for key in A.DECKS:
        for x in A.audit(key):
            if x["kind"] != "live_richer":
                continue
            dict_name = x.get("protected_by")
            if key != "aws" or not dict_name or x.get("escaped"):
                unprotectable.append((A.DECKS[key]["name"], x))
                continue
            name = by_guid.get(x["guid"])
            if not name:
                unprotectable.append((A.DECKS[key]["name"], x))
                continue
            updates[dict_name][name] = x["live"]

    n = sum(len(v) for v in updates.values())
    if not n:
        print("no foldable hand-edits — build source already has everything")
    else:
        for dict_name, adds in updates.items():
            if not adds:
                continue
            data = load_dict(dict_name)
            for k, v in adds.items():
                was = "updated" if k in data else "ADDED (was unprotected!)"
                bolds = v.count("<b>")
                print(f"  {dict_name}[{k!r}] {was} — {len(A.visible(v))}ch, {bolds} bold")
                data[k] = v
            f = write_dict(dict_name, data)
            print(f"  -> {len(data)} entries in {f}")

    if unprotectable:
        print("\n  !! CANNOT be protected by an override dict:")
        for deck, x in unprotectable:
            why = ("the builder HTML-escapes this field" if x.get("escaped")
                   else "no override dict exists for this field/deck")
            print(f"     [{deck}] {x['label']} / {x['field']} — {why}")
        print("     These stay only in the collection. A rebuild + import WILL lose them.")

    if DRY:
        print("\n--dry-run: nothing written")
        return

    if n:
        print("\nrebuilding AWS_Services.apkg ...")
        r = subprocess.run([A.ENV_PY, "build_deck_v2.py"], cwd=AWS["dir"],
                           capture_output=True, text=True)
        print("  " + (r.stdout.strip() or r.stderr.strip()))
        print("\nNow commit build_deck.py / build_deck_v2.py / AWS_Services.apkg.")
        print("Do NOT re-import the .apkg to update the collection — use /anki-sync push.")


if __name__ == "__main__":
    main()
