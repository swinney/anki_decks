"""Shared plumbing for /anki-sync: paths, the deck registry, and the audit engine."""

import os
import re
import html
import json
import glob
import time
import shutil
import sqlite3
import hashlib
import tempfile
import subprocess

HOME = os.path.expanduser("~")
REPO = "/Users/swinney/Projects/anki_decks"
COL = os.path.join(HOME, "Library/Application Support/Anki2/User 1/collection.anki2")
BACKUPS = os.path.join(HOME, "Library/Application Support/Anki2/User 1/backups")

# Two different interpreters, and they are NOT interchangeable:
#   ENV_PY  has genanki (builds decks). `conda run -n anki_decks python3` resolves
#           the WRONG python — always use this path directly.
#   ANKI_PY has the `anki` package (touches the collection) but NOT genanki.
ENV_PY = "/opt/homebrew/Caskroom/miniforge/base/envs/anki_decks/bin/python"
ANKI_PY = os.path.join(HOME, "Library/Application Support/AnkiProgramFiles/.venv/bin/python")

# guid prefix -> deck. `overrides` names the dicts that can protect a hand-edit;
# a deck with none cannot have edits folded back automatically.
DECKS = {
    "aws": {
        "name": "AWS::Services",
        "guid_prefix": "awscard-",
        "dir": f"{REPO}/AWS_certified_architect_associate/deck_versions",
        "builder": f"{REPO}/AWS_certified_architect_associate/deck_versions/build_deck_v2.py",
        "fields": ["Service", "Category", "Description", "Associated", "ServiceLink",
                   "Pick", "Confuse", "Scope", "BestPractices"],
        "label_field": 0,
        # field -> the dict in the build source that protects it
        "overrides": {"Description": "RICH_DESCRIPTIONS", "Service": "DISPLAY_NAMES"},
        # emitted through html.escape() by the builder, so hand-added markup CANNOT survive
        "escaped": ["Pick", "Confuse", "Scope"],
    },
    "supplement": {
        "name": "AWS Interview Supplement — HBS Stack",
        "guid_prefix": "hbssupp-",
        "dir": f"{REPO}/aws_interview_supplement/deck_versions",
        "builder": f"{REPO}/aws_interview_supplement/deck_versions/build_deck.py",
        "fields": ["Type", "Prompt", "Answer", "Points", "Services",
                   "Contrast", "Interview", "Acronyms"],
        "label_field": 1,
        "overrides": {},
        "escaped": ["Type", "Prompt", "Answer", "Points", "Contrast", "Interview", "Acronyms"],
    },
    "osi": {
        "name": "AWS::OSI Layers for AWS Solutions Architects",
        "guid_prefix": "osicard-",
        "dir": f"{REPO}/osi_layers_aws/deck_versions",
        "builder": f"{REPO}/osi_layers_aws/deck_versions/build_deck.py",
        "fields": ["Type", "Prompt", "Answer", "Layer", "Why", "Services",
                   "Contrast", "Exam", "Acronyms"],
        "label_field": 1,
        "overrides": {},
        "escaped": ["Type", "Prompt", "Answer", "Layer", "Why", "Contrast", "Exam", "Acronyms"],
    },
}


# ---------------------------------------------------------------- text helpers

def visible(s):
    """Rendered text: tags stripped, entities resolved, whitespace collapsed."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def cosmetic(a, b):
    """True when two fields differ only in markup/entity encoding.

    Anki normalises entities on import (' <-> &#x27;, ↗ <-> &#8599;), so a raw
    byte diff is a false positive. Compare what the card actually renders.
    """
    return a.strip() != b.strip() and visible(a) == visible(b)


def richness(s):
    """Rank two versions of a field. Bold count dominates: hand-edits add bold."""
    return (s.count("<b>"), len(visible(s)))


def aws_guid(name):
    return "awscard-" + hashlib.md5(name.encode()).hexdigest()[:12]


# ------------------------------------------------------------ reading the world

def expected_notes(key):
    """{guid: {fields, tags}} exactly as the builder would emit. Writes nothing."""
    d = DECKS[key]
    here = os.path.dirname(os.path.abspath(__file__))
    out = subprocess.run(
        [ENV_PY, os.path.join(here, "_extract.py"), d["dir"], d["builder"]],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise SystemExit(f"builder extraction failed for {key}:\n{out.stderr}")
    return json.loads(out.stdout)


def live_notes(prefix=None):
    """{guid: {fields, tags}} from the live collection.

    Reads a COPY, so this is safe with Anki running (audit is read-only). Any
    WRITE path must still go through anki_guard.assert_anki_closed().
    """
    tmp = tempfile.mktemp(suffix=".anki2")
    shutil.copy2(COL, tmp)
    con = sqlite3.connect(tmp)
    con.create_collation("unicase", lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))
    q = "SELECT guid, flds, tags FROM notes"
    if prefix:
        q += f" WHERE guid LIKE '{prefix}%'"
    out = {g: {"fields": f.split("\x1f"), "tags": sorted(t.split())}
           for g, f, t in con.execute(q)}
    con.close()
    os.unlink(tmp)
    return out


# ------------------------------------------------------------------- the audit

def audit(key):
    """Every field of every note: build vs collection. Returns a list of drifts."""
    d = DECKS[key]
    exp = expected_notes(key)
    live = live_notes(d["guid_prefix"])
    drifts = []

    for guid, e in exp.items():
        if guid not in live:
            drifts.append({"guid": guid, "label": e["fields"][d["label_field"]][:40],
                           "field": "-", "kind": "missing_from_collection"})
            continue
        lf, ef = live[guid]["fields"], e["fields"]
        for i, fname in enumerate(d["fields"]):
            if i >= len(lf) or i >= len(ef):
                continue
            if lf[i].strip() == ef[i].strip() or cosmetic(lf[i], ef[i]):
                continue
            live_richer = richness(lf[i]) > richness(ef[i])
            protected = fname in d["overrides"]
            drifts.append({
                "guid": guid,
                "label": visible(ef[d["label_field"]])[:40] or guid,
                "field": fname,
                "kind": "live_richer" if live_richer else "build_richer",
                "protected_by": d["overrides"].get(fname),
                "escaped": fname in d["escaped"],
                "live_len": len(visible(lf[i])), "live_bold": lf[i].count("<b>"),
                "build_len": len(visible(ef[i])), "build_bold": ef[i].count("<b>"),
                "live": lf[i], "build": ef[i],
            })

        if live[guid]["tags"] != e["tags"]:
            drifts.append({
                "guid": guid, "label": visible(ef[d["label_field"]])[:40],
                "field": "TAGS", "kind": "tags",
                "live": " ".join(live[guid]["tags"]), "build": " ".join(e["tags"]),
            })

    extra = set(live) - set(exp)
    for guid in extra:
        drifts.append({"guid": guid, "label": visible(live[guid]["fields"][0])[:40],
                       "field": "-", "kind": "not_in_build"})
    return drifts


# ----------------------------------------------------------------- write safety

def backup():
    """Timestamped copy of the collection. Call before EVERY write."""
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bak = COL + f".bak-{stamp}"
    shutil.copy2(COL, bak)
    for extra in glob.glob(COL + "-*"):
        shutil.copy2(extra, bak + os.path.splitext(extra)[1])
    print(f"backup -> {bak}")
    return bak


SCHED_SQL = "SELECT id, ivl, due, reps, lapses, queue, type FROM cards"


def sched_snapshot(col):
    return {r[0]: tuple(r[1:]) for r in col.db.all(SCHED_SQL)}


def assert_no_drift(before, after):
    """Prove a write touched no scheduling. Review history is the irreplaceable part."""
    drift = [c for c in before if before[c] != after.get(c)]
    print(f"cards with changed scheduling: {len(drift)} (expect 0)")
    if drift:
        raise SystemExit(f"SCHEDULING DRIFT on {len(drift)} cards — do NOT sync: {drift[:10]}")
