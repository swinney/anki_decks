#!/usr/bin/env python3
"""List, validate, and restore Anki's own auto-backups. Also: forensics.

Anki's `backups/*.colpkg` files are written BY Anki, so they are internally
consistent — the most trustworthy recovery source that exists. A file byte-copied
out from under a running Anki is not, even if it looks fine.

  recover.py                     list every backup, validated
  recover.py --restore <file>    install it as the live collection
  recover.py --trace <Service>   when did a field change, and to what?

`--trace` is the forensic tool: it walks the backups showing a field's visible
length and <b> count over time, which is how you find the exact moment an edit was
wiped and which version was yours.

Run with the CONDA env python (it has zstandard):
  .../envs/anki_decks/bin/python recover.py
"""
import io
import os
import re
import sys
import glob
import time
import shutil
import sqlite3
import hashlib
import zipfile
import tempfile
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ankilib as A                        # noqa: E402
from anki_guard import assert_anki_closed  # noqa: E402


def unpack(colpkg):
    """The real data lives in collection.anki21b (zstd). collection.anki2 is a stub."""
    import zstandard
    z = zipfile.ZipFile(colpkg)
    names = z.namelist()
    if "collection.anki21b" in names:
        raw = z.read("collection.anki21b")
        data = zstandard.ZstdDecompressor().stream_reader(io.BytesIO(raw)).read()
    else:
        data = z.read("collection.anki2")
    tmp = tempfile.mktemp(suffix=".anki2")
    open(tmp, "wb").write(data)
    return tmp


def probe(path):
    con = sqlite3.connect(path)
    con.create_collation("unicase", lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))
    out = {}
    try:
        out["integrity"] = con.execute("PRAGMA integrity_check").fetchone()[0]
        for k, q in [("notes", "SELECT count(*) FROM notes"),
                     ("cards", "SELECT count(*) FROM cards"),
                     ("revlog", "SELECT count(*) FROM revlog")]:
            out[k] = con.execute(q).fetchone()[0]
    except Exception as e:
        out["integrity"] = f"ERROR {e}"
    con.close()
    return out


def cmd_list():
    print("Anki's own auto-backups (written by Anki => internally consistent):\n")
    hdr = f"{'backup':34s} {'integrity':10s} {'notes':>7s} {'cards':>7s} {'revlog':>7s}"
    print(hdr)
    print("-" * len(hdr))
    for f in sorted(glob.glob(os.path.join(A.BACKUPS, "*.colpkg")))[-12:]:
        t = unpack(f)
        p = probe(t)
        os.unlink(t)
        print(f"{os.path.basename(f):34s} {str(p['integrity'])[:10]:10s} "
              f"{p.get('notes', 0):7} {p.get('cards', 0):7} {p.get('revlog', 0):7}")

    t = tempfile.mktemp(suffix=".anki2")
    shutil.copy2(A.COL, t)
    p = probe(t)
    os.unlink(t)
    print("-" * len(hdr))
    print(f"{'LIVE collection.anki2':34s} {str(p['integrity'])[:10]:10s} "
          f"{p.get('notes', 0):7} {p.get('cards', 0):7} {p.get('revlog', 0):7}")
    print("\nRevlog is the irreplaceable column — everything else rebuilds from source.")
    print("Restore:  recover.py --restore <backup-file>")


def cmd_restore(name):
    src = name if os.path.isabs(name) else os.path.join(A.BACKUPS, name)
    if not os.path.exists(src):
        sys.exit(f"not found: {src}")

    tmp = unpack(src)
    p = probe(tmp)
    print(f"candidate: {os.path.basename(src)}")
    print(f"  integrity={p['integrity']}  notes={p['notes']}  cards={p['cards']}  revlog={p['revlog']}")
    if p["integrity"] != "ok":
        sys.exit("REFUSING: candidate fails integrity_check")

    assert_anki_closed(A.COL)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    if os.path.exists(A.COL):
        bad = A.COL + f".CORRUPT-{stamp}"
        shutil.move(A.COL, bad)            # preserved, never deleted
        print(f"current collection preserved -> {os.path.basename(bad)}")
    for j in ("-wal", "-shm"):             # journals belong to the old db
        if os.path.exists(A.COL + j):
            shutil.move(A.COL + j, A.COL + f".CORRUPT-{stamp}{j}")

    shutil.copy2(tmp, A.COL)
    os.chmod(A.COL, 0o600)
    os.unlink(tmp)
    print(f"restored <- {os.path.basename(src)}")
    print("\nOpen Anki -> Tools -> Check Database. Then sync (UPLOAD if asked for a direction).")
    print("Note: changes made after this backup are gone — re-run /anki-sync push/pull.")


def cmd_trace(service):
    """Walk the backups showing how one card's fields changed over time."""
    guid = A.aws_guid(service)
    fields = A.DECKS["aws"]["fields"]
    print(f"tracing {service!r}  (guid {guid})\n")
    hdr = f"{'snapshot':26s} " + " ".join(f"{f[:11]:>12s}" for f in fields)
    print(hdr)
    print("-" * len(hdr))
    prev = None
    files = sorted(glob.glob(os.path.join(A.BACKUPS, "*.colpkg")))[-14:]
    for f in files + [A.COL]:
        label = ("LIVE (now)" if f == A.COL
                 else os.path.basename(f).replace("backup-", "").replace(".colpkg", ""))
        t = unpack(f) if f != A.COL else tempfile.mktemp(suffix=".anki2")
        if f == A.COL:
            shutil.copy2(A.COL, t)
        con = sqlite3.connect(t)
        row = con.execute("SELECT flds FROM notes WHERE guid=?", (guid,)).fetchone()
        con.close()
        os.unlink(t)
        if not row:
            print(f"{label:26s} (not present)")
            continue
        fl = row[0].split("\x1f")
        cells = []
        for i in range(len(fields)):
            v = fl[i] if i < len(fl) else ""
            star = "*" if prev and i < len(prev) and prev[i] != v else " "
            cells.append(f"{len(A.visible(v)):>5d}/{v.count('<b>'):<2d}{star}".rjust(12))
        prev = fl
        print(f"{label:26s} " + " ".join(cells))
    print("\n(len/bold per field;  * = changed from the previous snapshot)")


if __name__ == "__main__":
    if "--restore" in sys.argv:
        cmd_restore(sys.argv[sys.argv.index("--restore") + 1])
    elif "--trace" in sys.argv:
        cmd_trace(sys.argv[sys.argv.index("--trace") + 1])
    else:
        cmd_list()
