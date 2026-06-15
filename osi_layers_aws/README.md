# OSI Layers for AWS Solutions Architects — Anki deck

A 43-card deck that teaches the OSI 7-layer model the way an AWS Solutions
Architect needs it: **which AWS service operates at which layer, and what that
layer lets it do (or not do)**. It is built for SAA-C03 intuition, not textbook
memorization.

## What's on a card

Front: the card **type** badge + a prompt. Back:

- **Layer** – the OSI layer(s) involved (badge).
- **Answer** – the layer + the crux, in one line.
- **Why this layer** – what the layer enables or prevents.
- **AWS services** – the services involved, each linked to its AWS page.
- **Don't confuse with** – the close-pair contrast.
- **Exam angle** – how SAA-C03 phrases it.
- **Acronyms** – every acronym on the card, expanded (pinned to the bottom).

## Card types (≈ weighting toward Layers 3 / 4 / 7)

| Type | Count | What it drills |
|------|-------|----------------|
| Overview anchors | 7 | One per OSI layer: job, PDU, protocols, AWS services there. |
| Service → Layer | 20 | A single service (NLB, WAF, Direct Connect…) → its layer + consequences. |
| Contrast | 7 | ALB vs NLB vs GWLB, SG vs NACL, WAF vs Shield, CloudFront vs Global Accelerator… |
| Scenario → Service | 9 | A requirement → pick the layer/service. |

## Organization (tags, single deck)

Every card carries two hierarchical tags so you can study mixed or filter:

- **Layer:** `OSI::L1-Physical` … `OSI::L7-Application`
- **Type:** `type::overview` · `type::service` · `type::contrast` · `type::scenario`

To study just one layer: `tag:OSI::L4-Transport`. Just the close-pairs:
`tag:type::contrast`.

## Files

| File | Purpose |
|------|---------|
| `OSI_Layers_AWS.apkg` | Current deck — import this into Anki. |
| `deck_versions/build_deck.py` | All card data + the genanki build script. |

## Build

The shared conda env is at the repo root (`~/Projects/anki_decks/environment.yml`):

```bash
cd ~/Projects/anki_decks/osi_layers_aws/deck_versions
python build_deck.py   # writes ../OSI_Layers_AWS.apkg
```

Each card has a **stable GUID** derived from a short per-card key (not the
prompt wording), so re-importing an updated deck **updates** existing cards
instead of duplicating them — and you can reword a prompt without orphaning its
review history.

> Note: in this repo the conda env's `genanki` is reached via the env
> interpreter directly
> (`/opt/homebrew/Caskroom/miniforge/base/envs/anki_decks/bin/python`), since
> `conda run python3` can resolve to a different Python.
