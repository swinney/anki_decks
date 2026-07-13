# AWS Certified Solutions Architect – Associate (SAA-C03) Anki deck

An Anki deck covering 109 exam-relevant AWS services. Each card shows the
service name (linked to its AWS homepage) and category on the front; the back
adds a description, three SAA-C03 study fields, and links to commonly
associated services.

## Card back fields

- **Description** – what the service does.
- **Pick this when** (green) – the trigger/scenario that points to this service.
- **Don't confuse with** (orange) – the close-pair contrast the exam tests.
- **Resilience scope** (blue) – AZ / Regional / Global reach and Multi-AZ support.
- **Often associated with** – related services, each linked to its AWS page.
- **Best practices** – link to the AWS best-practices page for the service.

## Files

| File | Purpose |
|------|---------|
| `AWS_Services.apkg` | Current deck — import this into Anki. |
| `deck_versions/build_deck.py` | Base data module: service list, descriptions, URLs, associations. |
| `deck_versions/exam_fields.py` | The three SAA-C03 fields per service. |
| `deck_versions/best_practices.py` | Best-practices URL per service. |
| `deck_versions/build_deck_v2.py` | Builds the current deck from the three modules above. |
| `deck_versions/build_deck_v1.py` | First version's build script (links only, no exam fields). |
| `deck_versions/AWS_Services_v1.apkg` | v1 snapshot (no exam fields). |
| `deck_versions/AWS_Services_v2.apkg` | v2 snapshot (exam fields, 8-field note). |
| `deck_versions/AWS_Services_v3.apkg` | v3 snapshot (current; adds Best practices, 9-field note). |

## Environment setup

The shared conda env is defined at the repo root (`~/Projects/anki_decks/environment.yml`):

```bash
cd ~/Projects/anki_decks
conda env create -f environment.yml   # first time only
conda activate anki_decks
```

## Rebuilding the deck

```bash
conda activate anki_decks   # or: pip install genanki
cd deck_versions
python3 build_deck_v2.py   # writes AWS_Services.apkg
```

Each card has a stable ID derived from the service name, so re-importing an
updated deck **updates** existing cards instead of duplicating them — your
study progress is preserved.

## Focused study sessions

Cards on the HBS interview stack are tagged `stack::hbs` across **three** decks,
so one search gathers all of them (Anki tags cross deck boundaries):

| Deck | Tagged | Applied by |
|---|---|---|
| `AWS::Services` | 24 of 110 | `HBS_STACK` in `deck_versions/build_deck_v2.py` |
| `AWS Interview Supplement — HBS Stack` | 20 of 20 | every note, by construction |
| `AWS::OSI Layers for AWS SAs` | 24 of 43 | `HBS_KEYS` in `osi_layers_aws/deck_versions/build_deck.py` |

**Build the session:** Tools → Create Filtered Deck, search
`tag:stack::hbs -is:suspended`, limit 100. For an interview cram, **uncheck**
"Reschedule cards based on my answers" — you then see every card regardless of
due date, and *Empty* restores each card's original interval and due date, so
your real schedule is untouched. Leave it **checked** to study normally.

Useful searches:

```
tag:stack::hbs                                # the whole stack (68 cards)
tag:stack::hbs tag:tier::1                    # highest-yield interview cards
tag:stack::hbs tag:topic::networking          # subnets, EIP, security groups
tag:stack::hbs Category:Security              # IAM, KMS, ACM, GuardDuty, Shield, CloudTrail
tag:stack::hbs (Category:Compute or tag:topic::compute)   # compute, across decks
```

`Category` is a field on the `AWS Service Card v2` note type, so field-scoped
drill-downs work without rebuilding anything. `tier::` and `topic::` come from
the supplement deck.

Note that filtered decks skip suspended and buried cards, and a card can only
live in one filtered deck at a time — if a build comes back short, empty any
other filtered deck first.

## Versioning

Git history is now the source of truth for versions. The `deck_versions/`
snapshots are kept as convenient rollback artifacts; to revert, re-import the
desired `.apkg`, or `git checkout` an earlier commit.
