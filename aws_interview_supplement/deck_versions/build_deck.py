#!/usr/bin/env python3
"""AWS Interview Supplement (HBS stack) — Anki deck.

Cross-cutting, operational/architectural cards that the two recall decks don't
cover: the gaps flagged for the HBS interview (Terraform vs CloudFormation,
Security Groups in depth, AMI sharing) plus the highest-value interview gotchas
tied to HBS's stated stack (see the hbs-interview-stack memory).

Every card is tagged:
  - stack::hbs           (this whole deck is the HBS supplement)
  - tier::1 .. tier::5   (study priority: 1 = foundations ... 5 = specialized)
  - topic::<area>        (iac / networking / compute / identity / security /
                          data / observability / governance)

Build:  python build_deck.py   # writes ../AWS_Interview_Supplement.apkg
"""
import os
import html
import hashlib
import genanki

# ---- AWS homepages used in the Services field -----------------------------
CFN      = "https://aws.amazon.com/cloudformation/"
S3       = "https://aws.amazon.com/s3/"
DDB      = "https://aws.amazon.com/dynamodb/"
SVC_CAT  = "https://aws.amazon.com/servicecatalog/"
VPC      = "https://aws.amazon.com/vpc/"
EC2      = "https://aws.amazon.com/ec2/"
KMS      = "https://aws.amazon.com/kms/"
ECS      = "https://aws.amazon.com/ecs/"
ECR      = "https://aws.amazon.com/ecr/"
FARGATE  = "https://aws.amazon.com/fargate/"
IAM      = "https://aws.amazon.com/iam/"
COGNITO  = "https://aws.amazon.com/cognito/"
AURORA   = "https://aws.amazon.com/rds/aurora/"
RDS      = "https://aws.amazon.com/rds/"
CW       = "https://aws.amazon.com/cloudwatch/"
CT       = "https://aws.amazon.com/cloudtrail/"
GUARDDUTY= "https://aws.amazon.com/guardduty/"

# Each card: key, tier, topic, type, prompt, answer, points, services, contrast,
# interview, acronyms.
CARDS = [
    dict(key="tf-vs-cfn", tier="tier::1", topic="topic::iac", type="IaC contrast",
         prompt="Terraform vs CloudFormation — the differences an interviewer probes?",
         answer="Both declarative IaC. CloudFormation is AWS-native, AWS-only, with state managed by AWS. Terraform is HashiCorp's tool: multi-cloud, with state you manage explicitly.",
         points="CFN: free, deep AWS integration, native drift detection, change sets, StackSets for multi-account/region, automatic rollback on failure. Terraform: HCL, providers (multi-cloud + SaaS), reusable modules, plan/apply, and a state file that is the source of truth (must be stored and locked).",
         services=[("CloudFormation", CFN)],
         contrast="Drift: CFN detects it natively; Terraform surfaces it on the next plan. Rollback: CFN auto-rolls-back; Terraform leaves partial state for you to reconcile.",
         interview="They want you to reason about state ownership, drift, multi-account (StackSets vs TF workspaces/modules), and when each fits a team.",
         acronyms="IaC = Infrastructure as Code; CFN = CloudFormation; TF = Terraform; HCL = HashiCorp Configuration Language; SaaS = Software as a Service; AWS = Amazon Web Services."),

    dict(key="tf-state", tier="tier::1", topic="topic::iac", type="IaC concept",
         prompt="How do you manage Terraform state safely on AWS, and why does it matter?",
         answer="Store state remotely in a versioned, encrypted S3 bucket and lock it with a DynamoDB table so concurrent applies cannot corrupt it.",
         points="State maps resources to real-world objects and can contain secrets, so encrypt it (SSE-KMS) and lock it down. S3 gives a durable shared backend with versioning for recovery; DynamoDB provides the state lock (LockID) that serializes writes. Never commit state to git.",
         services=[("S3", S3), ("DynamoDB", DDB)],
         contrast="CloudFormation has no equivalent chore — AWS stores and locks stack state for you.",
         interview="A classic Terraform-on-AWS question that maps directly onto their S3 + DynamoDB usage. Mention locking, encryption, and least-privilege on the bucket.",
         acronyms="IaC = Infrastructure as Code; SSE-KMS = Server-Side Encryption with KMS; KMS = Key Management Service; S3 = Simple Storage Service; AWS = Amazon Web Services."),

    dict(key="cfn-service-catalog", tier="tier::5", topic="topic::governance", type="Governance",
         prompt="How do CloudFormation and Service Catalog work together?",
         answer="Service Catalog publishes approved CloudFormation templates as 'products' that users launch with constrained permissions — self-service with governance.",
         points="Admins define products (CFN templates), group them into portfolios, and attach launch constraints (a role users assume) and template constraints (allowed parameter values). End users launch vetted stacks without broad IAM rights. You get standardization, guardrails, versioning, and a curated menu instead of free-form CloudFormation.",
         services=[("Service Catalog", SVC_CAT), ("CloudFormation", CFN)],
         contrast="Raw CloudFormation: anyone with permissions deploys anything. Service Catalog: only vetted products, launched via least-privilege roles.",
         interview="They use Service Catalog — expect 'how do you let teams self-serve infra safely?' → portfolios, launch constraints, tagging, versioned products.",
         acronyms="CFN = CloudFormation; IAM = Identity and Access Management."),

    dict(key="subnet-public-private", tier="tier::1", topic="topic::networking", type="Networking",
         prompt="What actually makes a subnet 'public' vs 'private', and how do private instances reach the internet?",
         answer="A subnet is public if its route table sends 0.0.0.0/0 to an Internet Gateway. Private subnets route egress to a NAT Gateway instead — outbound only.",
         points="Public subnet + IGW route + a public/Elastic IP = inbound reachable. Private subnet has no IGW route; a NAT Gateway (itself in a public subnet) gives outbound-only access for patching and API calls, with no inbound. NAT GW is AZ-scoped, so run one per AZ for HA. 'Public/private' is a routing property, not a subnet checkbox.",
         services=[("VPC", VPC)],
         contrast="IGW = bidirectional public reachability; NAT Gateway = outbound-only egress for private subnets.",
         interview="A whiteboard staple: ALB in public subnets, app/DB tiers in private, NAT per AZ. Know why the DB tier has no internet route at all.",
         acronyms="VPC = Virtual Private Cloud; IGW = Internet Gateway; NAT = Network Address Translation; AZ = Availability Zone; IP = Internet Protocol; ALB = Application Load Balancer; DB = Database; API = Application Programming Interface; HA = High Availability."),

    dict(key="eip", tier="tier::1", topic="topic::networking", type="Networking",
         prompt="What is an Elastic IP, when do you use one, and what is the cost gotcha?",
         answer="A static public IPv4 address you own in your account and can remap between instances or NAT gateways. Use it when you need a fixed, portable public IP.",
         points="An EIP survives stop/start and instance replacement (unlike an auto-assigned public IP) and can be remapped for failover. Gotcha: AWS now charges hourly for all public IPv4, and idle/unattached EIPs cost extra — release what you do not use. Prefer DNS / a load balancer over handing out EIPs where you can.",
         services=[("VPC", VPC)],
         contrast="Auto-assigned public IP = ephemeral, changes on stop/start; EIP = persistent and movable.",
         interview="Probes cost-awareness (the IPv4 charges) and whether you reach for an EIP vs a load balancer or Route 53.",
         acronyms="EIP = Elastic IP; IP = Internet Protocol; IPv4 = Internet Protocol version 4; VPC = Virtual Private Cloud; DNS = Domain Name System; NAT = Network Address Translation; AWS = Amazon Web Services."),

    dict(key="sg-depth", tier="tier::1", topic="topic::networking", type="Networking",
         prompt="Security Groups in depth — the behaviors interviewers expect you to know?",
         answer="Instance/ENI-level, stateful, allow-only firewalls. Return traffic is automatically allowed, and there are no deny rules.",
         points="Rules can reference another security group (not just CIDRs) — e.g., 'allow 5432 from the app SG' so the DB opens only to app instances with no IP bookkeeping. Multiple SGs on one ENI are additive (most-permissive union). The default SG allows all intra-SG traffic. Use NACLs (stateless, subnet-level, deny-capable) only for coarse explicit denies.",
         services=[("VPC", VPC)],
         contrast="Security Group = stateful, instance-level, allow-only; NACL = stateless, subnet-level, allow + deny.",
         interview="Expect 'how do you lock the DB to just the app tier?' → a security group that references the app's security group. Know stateful vs stateless cold.",
         acronyms="SG = Security Group; ENI = Elastic Network Interface; CIDR = Classless Inter-Domain Routing; NACL = Network Access Control List; VPC = Virtual Private Cloud; DB = Database; IP = Internet Protocol."),

    dict(key="ami-sharing", tier="tier::2", topic="topic::compute", type="Compute gotcha",
         prompt="How do you share an AMI across accounts — and what is the encryption gotcha?",
         answer="Modify the AMI's launch permissions to add the target account, which also shares the backing EBS snapshots. If those snapshots are encrypted, you must share the KMS key too.",
         points="Encrypted snapshots cannot use the default aws/ebs key for cross-account sharing — encrypt with a customer-managed key (CMK) and grant the target account kms:DescribeKey / CreateGrant / ReEncrypt / Decrypt via the key policy. The target account should copy the AMI to re-encrypt it with its own key. Alternatives: share via AWS Organizations, or run a central golden-AMI account.",
         services=[("EC2", EC2), ("KMS", KMS)],
         contrast="Sharing the AMI is not the same as sharing the key — forget the KMS grant and the launch fails.",
         interview="A real gotcha for multi-account golden-AMI pipelines (likely how HBS standardizes EC2). Walk the KMS key-policy grant plus the copy-to-re-encrypt flow.",
         acronyms="AMI = Amazon Machine Image; EBS = Elastic Block Store; KMS = Key Management Service; CMK = Customer-Managed Key; EC2 = Elastic Compute Cloud; AWS = Amazon Web Services; HBS = Harvard Business School."),

    dict(key="golden-ami", tier="tier::2", topic="topic::compute", type="Compute concept",
         prompt="What is a 'golden AMI' pipeline, and how is image encryption handled?",
         answer="A pre-baked, hardened, patched base image produced by an automated pipeline (e.g., EC2 Image Builder), versioned and distributed so every instance launches from a known-good state.",
         points="Bake in OS hardening, agents, and patches for faster, consistent launches and a smaller attack surface. Encrypt the AMI's snapshots with a CMK; copy the AMI to re-encrypt or to share cross-account. Tag and version images and deprecate old ones. Pair with Systems Manager for ongoing patch compliance.",
         services=[("EC2", EC2)],
         contrast="Golden AMI (bake the image) vs configure-at-boot (user data / config management) — bake for speed and consistency, boot-config for flexibility.",
         interview="Shows you think about consistency, patching, and supply-chain hygiene at fleet scale.",
         acronyms="AMI = Amazon Machine Image; CMK = Customer-Managed Key; OS = Operating System; EC2 = Elastic Compute Cloud."),

    dict(key="ecs-roles", tier="tier::2", topic="topic::compute", type="Compute gotcha",
         prompt="ECS task role vs task execution role — what is the difference?",
         answer="The task role grants permissions your application code uses at runtime (e.g., read an S3 bucket). The execution role grants the ECS/Fargate agent the permissions to start the task (pull from ECR, write logs to CloudWatch, fetch secrets).",
         points="Two different principals: the agent (execution role) vs your container (task role). Common failures: the image will not pull or logs will not ship → the execution role is missing ECR/CloudWatch permissions; the app cannot reach AWS APIs → the task role is missing permissions. Keep both least-privilege and separate.",
         services=[("ECS", ECS), ("ECR", ECR)],
         contrast="Execution role = infrastructure plumbing (pull image, ship logs, fetch secrets); task role = what the application itself may do.",
         interview="An extremely common Fargate gotcha; they run ECS Fargate + ECR, so expect it.",
         acronyms="ECS = Elastic Container Service; ECR = Elastic Container Registry; S3 = Simple Storage Service; API = Application Programming Interface; AWS = Amazon Web Services."),

    dict(key="fargate-vs-ec2", tier="tier::2", topic="topic::compute", type="Compute contrast",
         prompt="ECS on Fargate vs the EC2 launch type — how do you choose?",
         answer="Fargate is serverless containers: AWS runs the hosts and you pay per task vCPU/memory. The EC2 launch type means you own and manage the cluster instances.",
         points="Fargate: no host patching or scaling, per-task isolation, simpler operations — but pricier per unit and less control (no host access, limited special hardware). EC2: cheaper at steady high utilization, custom/GPU instance types, host-level control — but you patch, scale, and secure the nodes. Capacity providers let you mix both.",
         services=[("Fargate", FARGATE), ("ECS", ECS)],
         contrast="Fargate = less ops, pay-per-task; EC2 launch type = more control and better economics at scale.",
         interview="They run Fargate — justify it (operational simplicity) and know when EC2 wins (cost at scale, GPU, special instances).",
         acronyms="ECS = Elastic Container Service; EC2 = Elastic Compute Cloud; vCPU = virtual Central Processing Unit; GPU = Graphics Processing Unit; AWS = Amazon Web Services."),

    dict(key="iam-policy-eval", tier="tier::1", topic="topic::identity", type="Identity",
         prompt="How does IAM decide whether a request is allowed?",
         answer="Default deny. An explicit Deny anywhere always wins; otherwise an explicit Allow is required, and any guardrail (SCP, permission boundary, session policy) must also allow it.",
         points="Order: explicit Deny > explicit Allow > implicit deny. Identity policies (on a user/role) vs resource policies (on an S3 bucket, KMS key, etc.) — cross-account access needs both sides to allow. SCPs cap the maximum permissions in an Organizations account; permission boundaries cap a role. Roles + STS assume-role give temporary credentials; an instance profile delivers a role to EC2.",
         services=[("IAM", IAM)],
         contrast="Identity policy = what this principal can do; resource policy = who can touch this resource. Cross-account = both required.",
         interview="Bread-and-butter. Know 'explicit deny wins' and the cross-account two-sided allow.",
         acronyms="IAM = Identity and Access Management; SCP = Service Control Policy; STS = Security Token Service; S3 = Simple Storage Service; KMS = Key Management Service; EC2 = Elastic Compute Cloud."),

    dict(key="kms-envelope", tier="tier::1", topic="topic::security", type="Security",
         prompt="Explain KMS envelope encryption, and key policy vs IAM.",
         answer="Envelope encryption: KMS generates a data key, you encrypt data locally with it, and store the KMS-encrypted data key beside the ciphertext. The KMS CMK never leaves KMS; it only wraps and unwraps data keys.",
         points="Efficient for large data — you never ship the bulk to KMS. Access needs both a key-policy grant and IAM; the key policy is authoritative (an empty key policy can lock out even admins). Grants give temporary, scoped key use. S3 SSE-KMS is envelope encryption with your CMK, adding CloudTrail auditability and per-key access control over SSE-S3.",
         services=[("KMS", KMS), ("S3", S3)],
         contrast="SSE-S3 = AWS-managed keys, simplest; SSE-KMS = your CMK, with access control and audit (plus cost/throttle considerations).",
         interview="Probes whether you understand why CMKs scale (data keys) and the key-policy-plus-IAM model.",
         acronyms="KMS = Key Management Service; CMK = Customer-Managed Key; IAM = Identity and Access Management; SSE = Server-Side Encryption; SSE-KMS = Server-Side Encryption with KMS; SSE-S3 = Server-Side Encryption with S3-managed keys; S3 = Simple Storage Service; AWS = Amazon Web Services."),

    dict(key="kms-cmk", tier="tier::1", topic="topic::security", type="Security",
         prompt="What is a KMS key (CMK), what are the three key types, and how does the key policy model work?",
         answer="A KMS key (formerly CMK — Customer Master Key) is a logical encryption key backed by HSMs inside KMS. The raw key material never leaves KMS; you interact through API calls (Encrypt, Decrypt, GenerateDataKey). Three types: AWS managed, customer managed, and customer managed with imported material.",
         points="AWS managed keys (aws/s3, aws/rds, etc.) are free, auto-rotated annually, and invisible — no key policy to write, but no cross-account sharing or custom rotation either. Customer managed keys ($1/month) give you full control: write a key policy, rotate on a schedule, share cross-account, set grants. Imported-material keys ($1/month) let you supply raw key bytes — you own the material and must re-import on rotation. Key policy is a resource-based policy on the key itself; BOTH the key policy AND the caller's IAM policy must allow an action for it to succeed. An overly restrictive (or empty default) key policy can lock out even the account root — always include an admin statement.",
         services=[("KMS", KMS)],
         contrast="AWS managed = simplest, no policy control, no cross-account; customer managed = full control + audit trail; SSE-KMS with a CMK adds CloudTrail visibility and per-key access control that SSE-S3 lacks.",
         interview="Nearly every HBS service (S3, RDS, Secrets Manager, EBS, SSM) can use KMS. Interviewers test whether you know the key-policy-plus-IAM dual-allow requirement — the #1 'access denied' surprise.",
         acronyms="CMK = Customer-Managed Key; KMS = Key Management Service; HSM = Hardware Security Module; IAM = Identity and Access Management; API = Application Programming Interface; ARN = Amazon Resource Name; SSE = Server-Side Encryption; SSE-KMS = Server-Side Encryption with KMS; SSE-S3 = Server-Side Encryption with S3-managed keys; AWS = Amazon Web Services."),

    dict(key="cognito-pools", tier="tier::3", topic="topic::identity", type="Identity contrast",
         prompt="Cognito User Pool vs Identity Pool — what does each do?",
         answer="A User Pool is the user directory: sign-up/sign-in, MFA, social/SAML federation, issuing JWT tokens. An Identity Pool exchanges a token for temporary AWS credentials so users can call AWS services directly.",
         points="Common pattern: authenticate against a User Pool, pass its token to an Identity Pool, and receive scoped IAM credentials (e.g., to a user-specific S3 prefix). The User Pool secures your app/API; the Identity Pool grants AWS access. They are independent and frequently combined.",
         services=[("Cognito", COGNITO)],
         contrast="User Pool = who the user is (authentication + tokens); Identity Pool = what AWS resources they may touch (temporary IAM credentials).",
         interview="They use Cognito — know the two-pool split and the token-to-credentials flow.",
         acronyms="MFA = Multi-Factor Authentication; SAML = Security Assertion Markup Language; JWT = JSON Web Token; IAM = Identity and Access Management; S3 = Simple Storage Service; API = Application Programming Interface; AWS = Amazon Web Services."),

    dict(key="dynamodb-design", tier="tier::2", topic="topic::data", type="Data",
         prompt="DynamoDB — the design knobs an interviewer expects (keys, capacity, indexes)?",
         answer="Model around access patterns: pick a partition key with high cardinality to spread load, optionally a sort key for ranges. Choose on-demand or provisioned capacity, and add GSIs/LSIs for alternate query patterns.",
         points="Hot partitions come from low-cardinality keys and cause throttling. On-demand suits spiky/unknown traffic (pay per request); provisioned (with auto scaling) is cheaper at steady load. A GSI has a different partition/sort key, its own capacity, and is eventually consistent; an LSI shares the partition key with a different sort key and must be created with the table. Single-table design is common; Streams + TTL handle events and expiry.",
         services=[("DynamoDB", DDB)],
         contrast="GSI = new partition key, addable anytime; LSI = same partition key, only at table creation.",
         interview="A NoSQL data-modeling question — lead with 'design from access patterns', then keys, capacity, and indexes.",
         acronyms="GSI = Global Secondary Index; LSI = Local Secondary Index; TTL = Time To Live; SQL = Structured Query Language; NoSQL = Not only SQL (non-relational)."),

    dict(key="aurora-vs-rds", tier="tier::2", topic="topic::data", type="Data contrast",
         prompt="Aurora vs standard RDS — what is different, and what is Serverless v2?",
         answer="Aurora is AWS's cloud-native MySQL/PostgreSQL-compatible engine with a distributed storage layer; RDS runs off-the-shelf engines on EBS. Aurora offers better performance, 6-way storage replication across 3 AZs, and up to 15 low-latency read replicas.",
         points="Aurora: auto-scaling storage (10 GB to 128 TB), fast failover, a reader endpoint, Global Database for cross-region, and Serverless v2 for fine-grained capacity auto-scaling. RDS: more engines (incl. Oracle, SQL Server, MariaDB) and is simpler/cheaper for modest needs. Both support Multi-AZ for HA, automated backups, and read replicas.",
         services=[("Aurora", AURORA), ("RDS", RDS)],
         contrast="Multi-AZ (a standby for failover/HA) vs read replicas (scale reads). Aurora replicas serve both roles.",
         interview="They run Aurora — know the storage architecture, the reader endpoint, and Serverless v2 vs provisioned.",
         acronyms="RDS = Relational Database Service; AZ = Availability Zone; EBS = Elastic Block Store; HA = High Availability; GB = Gigabyte; TB = Terabyte; SQL = Structured Query Language; AWS = Amazon Web Services."),

    dict(key="observability-quad", tier="tier::4", topic="topic::observability", type="Observability contrast",
         prompt="CloudWatch vs CloudTrail vs Config vs GuardDuty — who sees what?",
         answer="CloudWatch = metrics, logs, and alarms (operational telemetry). CloudTrail = the API-call audit log (who did what, when). Config = resource configuration state and compliance over time. GuardDuty = threat detection derived from logs.",
         points="Performance/health → CloudWatch. 'Who deleted the bucket?' → CloudTrail. 'Is this resource compliant / what changed?' → Config. 'Is something malicious happening?' → GuardDuty (which consumes CloudTrail, VPC Flow Logs, and DNS logs). Shield is a separate axis (DDoS). They share inputs but answer different questions.",
         services=[("CloudWatch", CW), ("CloudTrail", CT), ("GuardDuty", GUARDDUTY)],
         contrast="CloudWatch = telemetry; CloudTrail = audit; Config = compliance/drift; GuardDuty = threats; Shield = DDoS.",
         interview="They list CloudWatch, CloudTrail, GuardDuty, and Shield — be crisp on which tool answers which question.",
         acronyms="API = Application Programming Interface; VPC = Virtual Private Cloud; DNS = Domain Name System; DDoS = Distributed Denial of Service."),
]


def esc(s):
    return html.escape(s)


def stable_guid(key):
    return "hbssupp-" + hashlib.md5(key.encode()).hexdigest()[:12]


def services_html(services):
    return " &middot; ".join(
        f'<a href="{url}">{esc(label)} <span class="ext">&#8599;</span></a>'
        for label, url in services
    )


model = genanki.Model(
    1980150003,
    "AWS Interview Card",
    fields=[
        {"name": "Type"},
        {"name": "Prompt"},
        {"name": "Answer"},
        {"name": "KeyPoints"},
        {"name": "Services"},
        {"name": "Contrast"},
        {"name": "Interview"},
        {"name": "Acronyms"},
    ],
    templates=[{
        "name": "Card 1",
        "qfmt": '<div class="type">{{Type}}</div>'
                '<div class="prompt">{{Prompt}}</div>',
        "afmt": '''{{FrontSide}}<hr id="answer">
<div class="answer">{{Answer}}</div>
{{#KeyPoints}}<div class="row points"><span class="lab">Key points</span>{{KeyPoints}}</div>{{/KeyPoints}}
{{#Services}}<div class="row svc"><span class="lab">AWS services</span><div class="links">{{Services}}</div></div>{{/Services}}
{{#Contrast}}<div class="row confuse"><span class="lab">Don&#39;t confuse with</span>{{Contrast}}</div>{{/Contrast}}
{{#Interview}}<div class="row interview"><span class="lab">Interview angle</span>{{Interview}}</div>{{/Interview}}
{{#Acronyms}}<div class="acro-label">Acronyms</div><div class="acro">{{Acronyms}}</div>{{/Acronyms}}''',
    }],
    css='''.card { font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 17px; text-align: center; color: #232f3e; background: #fff; padding: 16px; }
.type { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #ec7211; font-weight: 700; }
.prompt { font-size: 20px; font-weight: 600; line-height: 1.4; margin: 8px auto; max-width: 600px; }
.answer { font-size: 17px; line-height: 1.5; margin: 12px auto; max-width: 600px; text-align: left; font-weight: 600; }
.row { text-align: left; max-width: 600px; margin: 10px auto; font-size: 15px; line-height: 1.5; border-left: 3px solid #d5dbdb; padding: 4px 0 4px 12px; }
.row .lab { display: block; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #687078; margin-bottom: 2px; }
.row.points { border-left-color: #687078; }
.row.svc { border-left-color: #0073bb; }
.row.confuse { border-left-color: #d85a30; }
.row.interview { border-left-color: #1d9e75; }
.links a { color: #0073bb; text-decoration: none; }
.links a:hover { text-decoration: underline; }
.ext { font-size: 12px; vertical-align: 1px; }
.acro-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #aab1b8; margin-top: 18px; }
.acro { font-size: 12px; line-height: 1.5; color: #98a0a8; margin: 4px auto 0; max-width: 600px; text-align: left; }
hr#answer { border: none; border-top: 1px solid #d5dbdb; margin: 14px 0; }''',
)

deck = genanki.Deck(1980150004, "AWS Interview Supplement — HBS Stack")


def main():
    keys = [c["key"] for c in CARDS]
    dupes = {k for k in keys if keys.count(k) > 1}
    if dupes:
        raise SystemExit(f"Duplicate card keys: {sorted(dupes)}")

    for c in CARDS:
        tags = ["stack::hbs", c["tier"], c["topic"]]
        note = genanki.Note(
            model=model,
            guid=stable_guid(c["key"]),
            tags=tags,
            fields=[
                esc(c["type"]),
                esc(c["prompt"]),
                esc(c["answer"]),
                esc(c.get("points", "")),
                services_html(c.get("services", [])),
                esc(c.get("contrast", "")),
                esc(c.get("interview", "")),
                esc(c.get("acronyms", "")),
            ],
        )
        deck.add_note(note)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "AWS_Interview_Supplement.apkg")
    genanki.Package(deck).write_to_file(out)
    print(f"Wrote {len(CARDS)} cards to {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
