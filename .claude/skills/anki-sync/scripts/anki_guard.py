"""Refuse to touch the collection while anything else has it open.

WHY THIS EXISTS — read before you "simplify" it:

The original guard in this repo was `pgrep -x Anki`. Anki does NOT run as a
process named "Anki". It runs as

    ~/Library/Application Support/AnkiProgramFiles/.venv/bin/python \
        -c "import aqt, sys; sys.argv[0]='Anki'; aqt.run()"

so `pgrep -x Anki`, `pgrep -i anki`, and `pgrep -f Anki.app` ALL return nothing
while Anki is wide open (`/Applications/Anki.app/Contents/MacOS/` holds only a
launcher). The guard silently passed, two processes wrote one SQLite file, and
the collection was corrupted — 86 notes lost and a broken index.

The authoritative question is not "is a process named Anki running" but "does any
other process hold this file open". `lsof` answers that regardless of process
name. The `aqt` command-line scan is a second, independent signal.

THE TRAP: Anki's interpreter is the SAME binary these scripts run under, so
matching on the python path alone false-positives on ourselves. Match on `aqt`
and exclude our own PID.

Never trust a negative from a check you have not seen return a positive. You can
test this one: launch Anki, run it, and confirm it aborts.
"""

import os
import sys
import subprocess


def _holders(col_path):
    """PIDs holding the collection (or its -wal/-shm) open, per lsof. Excludes self."""
    me = os.getpid()
    out = subprocess.run(
        ["lsof", "-F", "pn", "--", col_path, col_path + "-wal", col_path + "-shm"],
        capture_output=True, text=True,
    ).stdout
    pids, cur = set(), None
    for line in out.splitlines():
        if line.startswith("p"):
            cur = int(line[1:])
        elif line.startswith("n") and cur and cur != me:
            pids.add(cur)
    return sorted(pids)


def _anki_gui():
    """PIDs whose command line is the Anki GUI (it imports aqt)."""
    out = subprocess.run(["ps", "-Ao", "pid=,command="], capture_output=True, text=True).stdout
    hits = []
    for line in out.splitlines():
        if "aqt" in line and "AnkiProgramFiles" in line and "grep" not in line:
            pid = int(line.split()[0])
            if pid != os.getpid():
                hits.append((pid, line.strip()[:100]))
    return hits


def assert_anki_closed(col_path):
    holders = _holders(col_path)
    gui = _anki_gui()
    if holders or gui:
        msg = ["ABORT: the collection is IN USE — refusing to touch it."]
        for pid in holders:
            msg.append(f"  lsof: pid {pid} holds the collection open")
        for pid, cmd in gui:
            msg.append(f"  ps  : pid {pid} is the Anki GUI -> {cmd}")
        msg.append("")
        msg.append("Quit Anki (Cmd-Q), wait for it to fully exit, then re-run.")
        sys.exit("\n".join(msg))
    print("guard: collection not open by any process; no Anki GUI running")
