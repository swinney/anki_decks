#!/usr/bin/env python3
"""v2: AWS service Anki deck with SAA-C03 exam fields
(Pick this when / Don't confuse with / Resilience scope)."""
import os
import html
import hashlib
import genanki

from build_deck import SERVICES, URL, assoc_html
from exam_fields import EXAM
from best_practices import BEST_PRACTICES


def esc(s):
    return html.escape(s)


def stable_guid(name):
    # Deterministic per-service GUID so re-importing any version updates
    # the same card instead of creating duplicates.
    return "awscard-" + hashlib.md5(name.encode()).hexdigest()[:12]


model = genanki.Model(
    1607392320,  # SAME id as the deployed v2 note type — adding a field (last)
                 # updates the existing note type in place on re-import and keeps
                 # review history. A NEW id would make Anki reject notes whose
                 # GUIDs already exist under the old type ("note type changed").
    "AWS Service Card v2",
    fields=[
        {"name": "Service"},
        {"name": "Category"},
        {"name": "Description"},
        {"name": "Associated"},
        {"name": "ServiceLink"},
        {"name": "Pick"},
        {"name": "Confuse"},
        {"name": "Scope"},
        {"name": "BestPractices"},
    ],
    templates=[{
        "name": "Card 1",
        "qfmt": '<div class="svc"><a href="{{ServiceLink}}">{{Service}} '
                '<span class="ext">&#8599;</span></a></div>'
                '<div class="cat">{{Category}}</div>',
        "afmt": '''{{FrontSide}}<hr id="answer">
<div class="desc">{{Description}}</div>
<div class="row pick"><span class="lab">Pick this when</span>{{Pick}}</div>
<div class="row confuse"><span class="lab">Don&#39;t confuse with</span>{{Confuse}}</div>
<div class="row scope"><span class="lab">Resilience scope</span>{{Scope}}</div>
<div class="assoc-label">Often associated with</div>
<div class="assoc">{{Associated}}</div>
{{#BestPractices}}<div class="bp-label">Best practices</div>
<div class="bp"><a href="{{BestPractices}}">View AWS best practices <span class="ext">&#8599;</span></a></div>{{/BestPractices}}''',
    }],
    css='''.card { font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 17px; text-align: center; color: #232f3e; background: #fff; padding: 16px; }
.svc { font-size: 28px; font-weight: 700; }
.svc a { color: #ec7211; text-decoration: none; }
.svc a:hover { text-decoration: underline; }
.svc .ext { font-size: 16px; vertical-align: 1px; }
.cat { font-size: 13px; letter-spacing: 1px; text-transform: uppercase; color: #687078; margin-top: 4px; }
.desc { font-size: 16px; line-height: 1.5; margin: 12px auto; max-width: 560px; text-align: left; }
.row { text-align: left; max-width: 560px; margin: 10px auto; font-size: 15px; line-height: 1.45; border-left: 3px solid #d5dbdb; padding: 4px 0 4px 12px; }
.row .lab { display: block; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #687078; margin-bottom: 2px; }
.row.pick { border-left-color: #1d9e75; }
.row.confuse { border-left-color: #d85a30; }
.row.scope { border-left-color: #378add; }
.assoc-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #687078; margin-top: 16px; }
.assoc { font-size: 15px; line-height: 1.7; margin-top: 4px; }
.assoc a { color: #0073bb; text-decoration: none; }
.assoc a:hover { text-decoration: underline; }
.bp-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #687078; margin-top: 16px; }
.bp { font-size: 15px; line-height: 1.7; margin-top: 4px; }
.bp a { color: #0073bb; text-decoration: none; }
.bp a:hover { text-decoration: underline; }
hr#answer { border: none; border-top: 1px solid #d5dbdb; margin: 14px 0; }''',
)

deck = genanki.Deck(2059400110, "AWS Solutions Architect — Services")

missing_url = [n for n, *_ in SERVICES if n not in URL]
missing_exam = [n for n, *_ in SERVICES if n not in EXAM]
missing_bp = [n for n, *_ in SERVICES if n not in BEST_PRACTICES]
if missing_url:
    raise SystemExit(f"Missing URL: {missing_url}")
if missing_exam:
    raise SystemExit(f"Missing exam fields: {missing_exam}")
if missing_bp:
    raise SystemExit(f"Missing best-practices URL: {missing_bp}")

# Services in the HBS interview stack (see the hbs-interview-stack memory).
# Tagged `stack::hbs` so the user can build an Anki filtered deck
# (tag:stack::hbs) for focused interview study. Sub-features the user listed
# (subnets, EIP, AMIs/AMI sharing, security groups) live inside the VPC/EC2
# cards or the OSI deck, and Terraform has no card here — see README/notes.
HBS_STACK = {
    "IAM", "S3", "ACM", "KMS", "Route 53", "CloudWatch", "VPC", "EC2", "ELB",
    "ECS", "Fargate", "ECR", "Cognito", "DynamoDB", "RDS", "Aurora",
    "CloudFormation", "Lambda", "Service Catalog", "API Gateway", "GuardDuty",
    "Shield", "CloudTrail", "SageMaker",
}
service_names = {n for n, *_ in SERVICES}
unknown_hbs = HBS_STACK - service_names
if unknown_hbs:
    raise SystemExit(f"HBS_STACK names not found in SERVICES: {sorted(unknown_hbs)}")

for name, cat, desc, assoc in SERVICES:
    pick, confuse, scope = EXAM[name]
    note = genanki.Note(
        model=model,
        guid=stable_guid(name),
        tags=["stack::hbs"] if name in HBS_STACK else [],
        fields=[
            name, cat, desc, assoc_html(assoc), URL[name],
            esc(pick), esc(confuse), esc(scope), BEST_PRACTICES[name],
        ],
    )
    deck.add_note(note)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "AWS_Services.apkg")
genanki.Package(deck).write_to_file(out)
print(f"Wrote {len(SERVICES)} cards to {os.path.normpath(out)}")
