# AWS Interview Supplement — HBS Stack

A 16-card deck of the **cross-cutting, operational/architectural** material the
two recall decks don't cover — built to prep for an interview on Harvard
Business School's stated AWS stack. It fills the gaps flagged when prioritizing
that stack (Terraform vs CloudFormation, Security Groups in depth, AMI sharing)
plus the highest-value interview gotchas tied to the services HBS actually uses.

## What's on a card

Front: a card-**type** badge + a prompt. Back:

- **Answer** – the crux in one or two lines.
- **Key points** – the details/gotchas an interviewer probes.
- **AWS services** – linked to their AWS pages.
- **Don't confuse with** – the close-pair contrast.
- **Interview angle** – how the topic comes up and what they're really testing.
- **Acronyms** – every acronym on the card, expanded (pinned to the bottom).

## Cards (by topic)

| Topic | Cards |
|-------|-------|
| IaC | Terraform vs CloudFormation · Terraform state on S3 + DynamoDB · CloudFormation + Service Catalog |
| Networking | public vs private subnet · Elastic IP · Security Groups in depth |
| Compute | AMI sharing (cross-account + KMS) · golden AMI pipeline · ECS task vs execution role · Fargate vs EC2 launch type |
| Identity | IAM policy evaluation · Cognito User Pool vs Identity Pool |
| Security | KMS envelope encryption + key policy vs IAM |
| Data | DynamoDB key/capacity/index design · Aurora vs RDS (+ Serverless v2) |
| Observability | CloudWatch vs CloudTrail vs Config vs GuardDuty |
| Governance | (Service Catalog, see IaC) |

## Tags

Every card carries three hierarchical tags so it folds into the same filtered
study workflow as the other decks:

- `stack::hbs` – this whole deck is the HBS supplement.
- `tier::1` … `tier::5` – study priority (1 = foundations … 5 = specialized).
- `topic::<area>` – iac / networking / compute / identity / security / data /
  observability / governance / ml.

Study the foundations first: `tag:stack::hbs (tag:tier::1 OR tag:tier::2)`.

## Build

```bash
cd ~/Projects/anki_decks/aws_interview_supplement/deck_versions
python build_deck.py   # writes ../AWS_Interview_Supplement.apkg
```

Stable GUIDs (derived from a short per-card key) mean re-importing updates
existing cards instead of duplicating them.

> Note: reach the conda env's `genanki` via the env interpreter directly
> (`/opt/homebrew/Caskroom/miniforge/base/envs/anki_decks/bin/python`), since
> `conda run python3` can resolve to a different Python.
