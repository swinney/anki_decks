#!/usr/bin/env python3
"""Build a standalone Anki deck for learning the OSI 7-layer model.
Not AWS-specific. Multiple cards per layer plus overview/mnemonic cards."""
import os
import html
import hashlib
import genanki

MODEL_ID = 1980050007
DECK_ID = 2080500007


def esc(s):
    return html.escape(s)


def stable_guid(key):
    return "osi-" + hashlib.md5(key.encode()).hexdigest()[:12]


# Per-layer data. devices/examples = where it lives / typical hardware-software.
LAYERS = [
    {
        "n": 1, "name": "Physical", "color": "6B7280",
        "function": "Transmits raw bits as electrical, optical, or radio signals over the physical medium; defines cables, connectors, voltages, pinouts, and data rates.",
        "clue": "moving raw bits (1s and 0s) as signals over a cable, fiber, or radio",
        "pdu": "Bit (the raw stream of 1s and 0s; sometimes called a symbol).",
        "protocols": "Ethernet physical layer (100BASE-T, 1000BASE-T), RJ45/twisted pair, fiber optics, DSL, USB, Bluetooth radio, IEEE 802.11 radio (Wi-Fi PHY).",
        "devices": "Cables, hubs, repeaters, modems, media converters, transceivers, and the physical NIC/port.",
    },
    {
        "n": 2, "name": "Data Link", "color": "B45309",
        "function": "Node-to-node delivery on the same local network: frames the bits, uses MAC (Media Access Control) addresses, and detects errors with a frame checksum (CRC).",
        "clue": "node-to-node delivery on one local link using MAC addresses and framing",
        "pdu": "Frame.",
        "protocols": "Ethernet (MAC), Wi-Fi (IEEE 802.11), PPP (Point-to-Point Protocol), ARP (Address Resolution Protocol, IP↔MAC), VLAN tagging (802.1Q), switching. Two sublayers: LLC and MAC.",
        "devices": "Switches, bridges, wireless access points, and the NIC (which holds the MAC address).",
    },
    {
        "n": 3, "name": "Network", "color": "1D4ED8",
        "function": "Logical addressing and routing of packets between different networks; picks the best path across interconnected networks.",
        "clue": "logical addressing (IP) and routing packets between separate networks",
        "pdu": "Packet.",
        "protocols": "IP (IPv4, IPv6), ICMP (ping/traceroute), IPsec, and routing protocols like OSPF and BGP.",
        "devices": "Routers and Layer-3 switches.",
    },
    {
        "n": 4, "name": "Transport", "color": "047857",
        "function": "End-to-end delivery between processes: segmentation/reassembly, port addressing, plus reliability, flow control, and congestion control (for TCP).",
        "clue": "end-to-end delivery between programs, with ports, reliability, and flow control",
        "pdu": "Segment (TCP) or Datagram (UDP).",
        "protocols": "TCP (Transmission Control Protocol — reliable, ordered) and UDP (User Datagram Protocol — fast, connectionless). Port numbers live here.",
        "devices": "Implemented in the host operating system's network stack (and inspected by L4 load balancers/firewalls).",
    },
    {
        "n": 5, "name": "Session", "color": "7C3AED",
        "function": "Establishes, manages, synchronizes, and tears down sessions (dialogs) between applications; adds checkpoints so long transfers can resume.",
        "clue": "opening, maintaining, and closing a conversation (session) between two apps",
        "pdu": "Data.",
        "protocols": "NetBIOS, RPC (Remote Procedure Call), PPTP, SAP; session setup/teardown and dialog control (sockets sit at the L4/L5 boundary).",
        "devices": "Application/session software on the hosts (no dedicated hardware).",
    },
    {
        "n": 6, "name": "Presentation", "color": "DB2777",
        "function": "Translates data between the application and the network: character encoding, serialization/format, compression, and encryption/decryption.",
        "clue": "translating data format — encoding, compression, and encryption",
        "pdu": "Data.",
        "protocols": "Encryption via TLS/SSL; formats and codecs like ASCII, Unicode, JPEG, GIF, MPEG; MIME; serialization.",
        "devices": "Codecs/encryption libraries in application software (no dedicated hardware).",
    },
    {
        "n": 7, "name": "Application", "color": "DC2626",
        "function": "The layer closest to the user: provides network services directly to applications (web, mail, file transfer, name resolution).",
        "clue": "the user-facing layer providing network services to applications",
        "pdu": "Data.",
        "protocols": "HTTP/HTTPS, FTP, SMTP, IMAP/POP3, DNS, DHCP, SSH, Telnet, SNMP.",
        "devices": "Applications and application-layer gateways/proxies (e.g., a web app, mail client, or L7 proxy).",
    },
]

# Overview / cross-cutting cards: (key, front, back, extra)
OVERVIEW = [
    ("mnemonic-up",
     "Mnemonic for the OSI layers <b>bottom-up</b> (Layer 1 → 7)?",
     "<b>Please Do Not Throw Sausage Pizza Away</b>",
     "Physical · Data Link · Network · Transport · Session · Presentation · Application"),
    ("mnemonic-down",
     "Mnemonic for the OSI layers <b>top-down</b> (Layer 7 → 1)?",
     "<b>All People Seem To Need Data Processing</b>",
     "Application · Presentation · Session · Transport · Network · Data Link · Physical"),
    ("order-up",
     "List the 7 OSI layers in order, <b>1 → 7</b>.",
     "1 Physical → 2 Data Link → 3 Network → 4 Transport → 5 Session → 6 Presentation → 7 Application",
     "Bottom (hardware) to top (user)."),
    ("order-down",
     "List the 7 OSI layers in order, <b>7 → 1</b>.",
     "7 Application → 6 Presentation → 5 Session → 4 Transport → 3 Network → 2 Data Link → 1 Physical",
     "Top (user) to bottom (hardware)."),
    ("pdu-summary",
     "What is the PDU (Protocol Data Unit) at each OSI layer?",
     "L1 <b>bits</b> · L2 <b>frames</b> · L3 <b>packets</b> · L4 <b>segments/datagrams</b> · L5–L7 <b>data</b>",
     "Mnemonic for L1–L4: \"Some People Fear Birthdays\" reversed — or just remember bits→frames→packets→segments."),
    ("encapsulation",
     "What is encapsulation in the OSI model?",
     "As data travels <b>down</b> the sender's stack, each layer wraps it with its own header (and L2 adds a trailer); the receiver <b>de-encapsulates</b> back up the stack.",
     "Each layer talks to its peer layer on the other host using the header it added."),
    ("osi-vs-tcpip",
     "How do the OSI layers map to the 4-layer TCP/IP model?",
     "TCP/IP <b>Application</b> = OSI 5–7 · <b>Transport</b> = OSI 4 · <b>Internet</b> = OSI 3 · <b>Link/Network Access</b> = OSI 1–2.",
     "TCP/IP collapses Session/Presentation/Application into one and Physical/Data Link into one."),
    ("layer-of-tcp",
     "At which OSI layer do TCP and UDP operate, and what do they add?",
     "Layer 4 (Transport). TCP adds reliability, ordering, and flow control; UDP is connectionless and fast. Both use <b>port numbers</b>.",
     ""),
    ("layer-of-ip",
     "At which OSI layer does IP (and routing) operate?",
     "Layer 3 (Network) — logical IP addressing and routing packets between networks.",
     ""),
    ("layer-of-mac",
     "At which OSI layer do MAC addresses and switches operate?",
     "Layer 2 (Data Link) — MAC addressing, framing, and switching within a local network.",
     ""),
]

MODEL = genanki.Model(
    MODEL_ID,
    "OSI Layer Card",
    fields=[
        {"name": "Header"},
        {"name": "Front"},
        {"name": "Back"},
        {"name": "Extra"},
        {"name": "Color"},
    ],
    templates=[{
        "name": "Card 1",
        "qfmt": '<div class="hdr" style="background:{{Color}}">{{Header}}</div>'
                '<div class="q">{{Front}}</div>',
        "afmt": '<div class="hdr" style="background:{{Color}}">{{Header}}</div>'
                '<div class="q">{{Front}}</div><hr id="answer">'
                '<div class="a">{{Back}}</div>'
                '{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}',
    }],
    css='''.card { font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 18px; color: #1f2430; background: #fff; text-align: center; padding: 18px; }
.hdr { display: inline-block; color: #fff; font-size: 13px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 5px 14px; border-radius: 14px; margin-bottom: 14px; }
.q { font-size: 20px; line-height: 1.45; max-width: 600px; margin: 0 auto; }
.a { font-size: 18px; line-height: 1.5; max-width: 600px; margin: 10px auto 0; }
.extra { font-size: 14px; color: #5f6671; line-height: 1.5; max-width: 600px; margin: 12px auto 0; font-style: italic; }
hr#answer { border: none; border-top: 1px solid #d9dde3; margin: 14px 0; }''',
)

deck = genanki.Deck(DECK_ID, "OSI Model — 7 Layers")


def add(key, header, front, back, extra, color, tags):
    deck.add_note(genanki.Note(
        model=MODEL, guid=stable_guid(key),
        fields=[header, front, back, extra, color], tags=tags,
    ))


for L in LAYERS:
    n, name, color = L["n"], L["name"], L["color"]
    ltag = f"OSI::L{n}_{name.replace(' ', '_')}"
    hdr = f"Layer {n} · {name}"
    add(f"L{n}-function", hdr, f"What is <b>OSI Layer {n}</b> — its name and primary function?",
        f"<b>{esc(name)}</b><br>{esc(L['function'])}", "", color, [ltag, "type::function"])
    add(f"L{n}-reverse", hdr, f"Which OSI layer handles: <i>{esc(L['clue'])}</i>?",
        f"<b>Layer {n} — {esc(name)}</b>", "", color, [ltag, "type::identify"])
    add(f"L{n}-pdu", hdr, f"What is the PDU (Protocol Data Unit) at Layer {n} ({esc(name)})?",
        esc(L["pdu"]), "", color, [ltag, "type::pdu"])
    add(f"L{n}-protocols", hdr, f"Key protocols / standards at Layer {n} ({esc(name)})?",
        esc(L["protocols"]), "", color, [ltag, "type::protocols"])
    add(f"L{n}-devices", hdr, f"Where does Layer {n} ({esc(name)}) live — typical devices / components?",
        esc(L["devices"]), "", color, [ltag, "type::devices"])

for key, front, back, extra in OVERVIEW:
    add(f"OV-{key}", "OSI Overview", front, back, extra, "111827", ["OSI::Overview", "type::concept"])

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "OSI_Layers.apkg")
    genanki.Package(deck).write_to_file(out)
    print(f"Wrote {len(deck.notes)} cards to {os.path.normpath(out)}")
