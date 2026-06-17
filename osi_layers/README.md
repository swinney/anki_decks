# OSI Model — 7 Layers (Anki deck)

A standalone, **vendor-neutral** deck for learning the OSI (Open Systems
Interconnection) 7-layer model. No AWS content — just the layers, what they do,
and how to remember them.

## What's inside (45 cards)

**Five cards per layer** (Physical → Application), each hitting a different angle:

- **Function** — the layer's name and primary job.
- **Identify** — given a description, name the layer (reverse recall).
- **PDU** — the Protocol Data Unit at that layer (bit, frame, packet, …).
- **Protocols** — key protocols/standards that operate there.
- **Devices** — where the layer lives / typical hardware or components.

**Ten overview cards** — the bottom-up and top-down mnemonics, layer order both
directions, the PDU summary, encapsulation, the OSI ↔ TCP/IP mapping, and quick
"which layer is TCP / IP / MAC?" recalls.

## Tags

- `OSI::L1_Physical` … `OSI::L7_Application` — filter to one layer.
- `OSI::Overview` — the cross-cutting cards.
- `type::function` · `type::identify` · `type::pdu` · `type::protocols` ·
  `type::devices` · `type::concept` — filter by card kind.

Each card is color-coded by layer for quick visual orientation.

## Building

```bash
conda activate anki_decks      # or: pip install genanki
cd deck_versions
python3 build_osi_deck.py      # writes ../OSI_Layers.apkg
```

Card GUIDs are derived deterministically from a stable key (layer + card type),
so re-importing an updated deck **updates** existing cards in Anki instead of
duplicating them — your review history is preserved.
