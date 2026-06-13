# AWS SAA-C03 Study Guide — Companion Notes

Deeper-dive notes that go **beyond** the Anki deck. The deck is for fast recall
of *what a service is* and *when to pick it*; this guide is for the "I need to
actually understand this" moments — concepts, trade-offs, and how a topic shows
up in real architecture decisions.

## How to use this guide

- Each topic follows the same template (see below) so it stays scannable.
- Two scenario types accompany each topic: a **greenfield design** decision and
  a **lift-and-shift / migration** decision, since the exam frames questions
  both ways.
- Add new topics under [Topics](#topics) and link them in the table of contents.

### Topic template

```markdown
### <Topic name>

**Concept** — plain-language explanation.
**Why it matters** — the practical payoff.
**Exam angle** — the distinctions/"don't confuse with" the exam tests.

**Scenario — design:** <new-build situation and the right call>
**Scenario — lift & shift:** <migration situation and the right call>

**Resources:** links.
```

## Table of contents

- [Networking & Content Delivery](#networking--content-delivery)
  - [Anycast IPs & AWS Global Accelerator](#anycast-ips--aws-global-accelerator)
  - [BGP — Border Gateway Protocol](#bgp--border-gateway-protocol)
  - [AWS Cloud Map](#aws-cloud-map)
- [Analytics](#analytics)
  - [Amazon Data Firehose](#amazon-data-firehose)
- [Management & Governance](#management--governance)
  - [AWS Control Tower](#aws-control-tower)
- [Developer Tools](#developer-tools)
  - [AWS X-Ray](#aws-x-ray)
- [Machine Learning & AI](#machine-learning--ai)
  - [Amazon Textract](#amazon-textract)

---

## Topics

## Networking & Content Delivery

### Anycast IPs & AWS Global Accelerator

**Concept** — *Anycast* is an addressing method where the **same IP (Internet Protocol) address is
advertised from many locations at once**, and internet routing via BGP (Border
Gateway Protocol) delivers
each user to the *nearest* one. Contrast with **unicast** (the normal case),
where one IP maps to one server in one place: a user in Tokyo hitting a unicast
IP in Virginia sends packets all the way to Virginia. With anycast, that same IP
is announced from Tokyo, Frankfurt, and Virginia simultaneously, and each user's
traffic enters at whichever site is closest in network terms — same destination
IP, different physical endpoint.

**Why it matters**

- **Lower latency** — traffic enters the provider's backbone at the nearest
  point of presence instead of crossing the public internet to a distant region.
- **Availability & failover** — if one location goes down, BGP simply routes to
  the next-nearest one.
- **DDoS (Distributed Denial of Service) resilience** — an attack is spread across many sites rather than
  concentrated on a single server.
- **Stable entry point** — you get a fixed IP that "follows" the user
  geographically.

**AWS Global Accelerator** (GA) is AWS's anycast offering: it gives you **two static
anycast IP addresses** that act as a fixed front door. Users connect to the
nearest AWS edge location via those IPs, then traffic rides the **AWS backbone**
to your application in whichever Region is healthiest — with fast, sub-minute
failover.

**Exam angle — don't confuse with:**

- **vs CloudFront** — CloudFront *caches* HTTP/HTTPS (Hypertext Transfer
  Protocol / Secure) content at the edge. Global Accelerator does **not** cache;
  it just gets any **TCP/UDP** (Transmission Control Protocol / User Datagram
  Protocol) traffic onto the AWS network fast and fails over quickly. Reach for
  GA for non-HTTP protocols, gaming, IoT (Internet of Things), VoIP (Voice over
  IP), or when you need static IPs; reach for CloudFront for
  cacheable web content.
- **vs Route 53 latency/geo routing** — Route 53 steers users by handing back
  *different IPs* in DNS (Domain Name System) responses (subject to DNS
  caching/TTL, Time To Live). GA steers users
  with a *single shared anycast IP*, so failover isn't gated on DNS propagation.
- **vs Standard unicast + DNS** — DNS-based steering gives different users
  different addresses; anycast achieves steering with one address.

**Scenario — design:** You're building a real-time multiplayer game backend on
NLBs (Network Load Balancers) in `us-east-1` and `ap-northeast-1`. Players worldwide need the lowest
possible latency over UDP and a single stable endpoint to hard-code in the
client. → **Global Accelerator**: two static anycast IPs, edge ingress onto the
AWS backbone, automatic routing to the nearest healthy Region. CloudFront
wouldn't fit (non-cacheable UDP), and Route 53 alone leaves you exposed to DNS
TTL during failover.

**Scenario — lift & shift:** You migrate a legacy on-prem application whose
clients have a firewall allowlist of **specific IP addresses** baked in and
can't be easily changed. You still want multi-Region resilience after the move.
→ **Global Accelerator** gives you two fixed anycast IPs to put on the allowlist
once, while you remain free to change, scale, or fail over the backend Regions
behind them without ever touching the client config.

**Resources:**

- [Global Accelerator — product page](https://aws.amazon.com/global-accelerator/)
- [Global Accelerator — Developer Guide: What is AGA?](https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html)
- [Global Accelerator vs CloudFront (FAQ)](https://aws.amazon.com/global-accelerator/faqs/)
- [CloudFront — product page](https://aws.amazon.com/cloudfront/)
- [Route 53 routing policies](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)

### BGP — Border Gateway Protocol

**Concept** — BGP is the routing protocol that runs the internet — think of it
as the internet's postal service, choosing how data gets from one network to
another. The internet isn't one network but thousands of independently operated
ones called **Autonomous Systems (AS)**, owned by Internet Service Providers
(ISPs), large enterprises, and cloud providers. BGP is how those systems
advertise to each other which IP address ranges they can reach, so a packet can
hop network-to-network all the way to its destination. Crucially, it selects
paths by configured **policy** (peering and business rules), not simply the
shortest physical distance. It does three things:

- **Path selection** — evaluates available routes and picks the best per policy.
- **Route advertisement** — routers announce the IP ranges they can reach.
- **Policy control** — operators prioritize, avoid, or balance routes.

Two flavors: **eBGP (external BGP)** exchanges routes *between* different
Autonomous Systems (e.g., your ISP to a neighboring ISP); **iBGP (internal
BGP)** shares routes *within* a single AS.

**Why it matters** — BGP is what makes dynamic, resilient routing possible: it
supports **multihoming** (connecting to multiple ISPs for redundancy) and
automatically updates routing tables when a link fails. The flip side is that a
misconfigured BGP advertisement can trigger large-scale internet outages. In
AWS, BGP is the mechanism behind anycast (Global Accelerator) and behind dynamic
routing on hybrid connectivity.

**Exam angle — where BGP shows up:**

- **Direct Connect and Site-to-Site VPN use BGP** for *dynamic* routing — routes
  are exchanged and failover happens automatically. Contrast with **static
  routing** on a VPN, where you hand-configure routes and there's no automatic
  reconvergence.
- **vs static routes** — BGP adapts when a path dies; static routes don't.
- **Underpins anycast / Global Accelerator** — the "route to the nearest healthy
  location" behavior of anycast is BGP doing path selection (see
  [Anycast IPs & AWS Global Accelerator](#anycast-ips--aws-global-accelerator)).

**Scenario — design:** You're building hybrid connectivity with a primary
**Direct Connect** link and a **Site-to-Site VPN** as backup, and you want
traffic to fail over automatically if Direct Connect drops. → Run **BGP** on
both connections and advertise the same prefixes with path preferences; BGP
reroutes to the VPN on failure with no manual route changes.

**Scenario — lift & shift:** You migrate an on-prem network that already
**multihomes across two ISPs** using BGP and its own AS number. Connecting to
AWS over Direct Connect, you keep using BGP to exchange routes dynamically,
preserving the redundancy model you already operate.

**Resources:**

- [AWS — What is BGP?](https://aws.amazon.com/what-is/border-gateway-protocol/)
- [Cloudflare — What is BGP?](https://www.cloudflare.com/learning/security/glossary/what-is-bgp/)
- [Direct Connect — routing policies and BGP communities](https://docs.aws.amazon.com/directconnect/latest/UserGuide/routing-and-bgp.html)
- [Site-to-Site VPN — routing options (static vs BGP)](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPNRoutingTypes.html)

### AWS Cloud Map

**Concept** — Cloud Map is a **service-discovery registry** for your
application's resources. You register components — microservices, databases,
queues, or any resource — under friendly logical names, and your application
**resolves them by name to get their current location** as they change
dynamically (scaling events, redeploys, failovers). It supports two discovery
methods: **DNS-based** (Cloud Map creates and manages the Route 53 records for
you) and **API-based** (Application Programming Interface) via the
`DiscoverInstances` call, which can return **health-aware** results and works
for **non-IP resources** (e.g., a queue URL or table name) with custom
attributes attached.

**Why it matters** — In dynamic microservice architectures, endpoints change
constantly, so hardcoding IPs or URLs breaks. Cloud Map is the single
source of truth for "what's running where, right now," letting services find
each other by logical name and automatically filtering out unhealthy instances.
**ECS Service Discovery is built on Cloud Map** — registering and deregistering
tasks for you as they start and stop.

**Exam angle — don't confuse with:**

- **vs Route 53** — the key distinction. Route 53 is **DNS**: it resolves names
  to IPs for internet/VPC routing. Cloud Map is an **application-level service
  registry** — it can track **non-IP** resources and arbitrary attributes, is
  queryable via API with health filtering, and uses Route 53 under the hood only
  for its DNS-based mode. Keyword cues: *"service discovery for microservices /
  register resources and resolve by name / dynamic endpoints"* → Cloud Map;
  *"domain names / hosted zones / DNS routing policies"* → Route 53.
- **vs App Mesh** — App Mesh is the **service mesh** (traffic routing,
  retries, observability via Envoy proxies); Cloud Map is the **discovery**
  layer it can pull endpoints from. Mesh = how traffic flows; Cloud Map = where
  things are.
- **vs ELB** — a load balancer *distributes* traffic across registered targets;
  Cloud Map *names and discovers* resources. They solve different problems.

**Scenario — design:** You're building microservices on **ECS** that scale up
and down continuously and need to call each other without hardcoded addresses.
→ Enable **ECS Service Discovery** (backed by **Cloud Map**): each service
registers under a name, callers resolve the current healthy endpoints by name,
and deregistration is automatic as tasks cycle.

**Scenario — lift & shift:** You migrate an app that relied on a self-managed
service registry (e.g., Consul or Eureka) or hardcoded host lists. → Register
the components in **Cloud Map** and resolve them by name via DNS or the
`DiscoverInstances` API, retiring the self-operated registry while keeping the
discover-by-name pattern the app already expects.

**Resources:**

- [AWS Cloud Map — product page](https://aws.amazon.com/cloud-map/)
- [What is AWS Cloud Map? (Developer Guide)](https://docs.aws.amazon.com/cloud-map/latest/dg/what-is-cloud-map.html)
- [ECS service discovery with Cloud Map](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html)

## Analytics

### Amazon Data Firehose

**Concept** — Amazon Data Firehose (formerly Kinesis Data Firehose) is the
**fully managed, no-code way to load streaming data into a destination** — S3,
Redshift, OpenSearch, or third parties like Splunk — in **near real time**. You
point a stream at a source, optionally transform/convert records in flight (e.g.
via a Lambda function or to Parquet), and Firehose **buffers** by size or time
and writes batches to the destination. There are no shards to size, no
consumers to run, and no servers to manage — it auto-scales to throughput.

**Why it matters** — It removes the "last mile" plumbing of a streaming
pipeline. Instead of writing and operating a consumer application to read a
stream and persist it, you get **delivery-as-a-service** with built-in
buffering, retry, optional compression/format conversion, and direct
integrations to analytics stores. That makes it the default glue for
"streaming-data → data lake / warehouse" ingestion.

**Exam angle — don't confuse with:**

- **vs Kinesis Data Streams (KDS)** — the key SAA distinction. KDS is a
  *durable, replayable stream* you build **custom real-time consumers** against
  (multiple readers, ordering, ~configurable retention). Firehose is **managed
  delivery to a destination** — no consumers, no replay, no per-record
  random access. Keyword cues: *"load/deliver into S3/Redshift/OpenSearch with
  no code"* → Firehose; *"custom real-time processing / multiple consumers /
  replay"* → Data Streams.
- **vs Amazon MSK (Managed Streaming for Apache Kafka) / Kinesis generally** — MSK is managed Apache Kafka for teams
  that need Kafka itself; Firehose is not a streaming platform, it's a loader.
- **vs Lambda-only pipelines** — you *can* hand-roll ingestion with Lambda, but
  Firehose owns the buffering/batching/retry so you don't operate it.

**Scenario — design:** You're building clickstream analytics for a new web app.
Events must land in an S3 data lake (and a Redshift table) for near-real-time
dashboards, and the team doesn't want to run streaming consumers. → **Amazon
Data Firehose**: ingest the events, convert to Parquet, buffer, and deliver to
S3 + Redshift with no consumer code. Reach for **Data Streams** only if you also
need custom real-time processing or replay of the raw events.

**Scenario — lift & shift:** You migrate an on-prem logging pipeline that ships
application logs to a search cluster. → Send logs to **Firehose** with delivery
to **OpenSearch** (with S3 backup of raw records), replacing the
self-managed forwarders/buffering layer with a managed stream you don't operate.

**Resources:**

- [Amazon Data Firehose — product page](https://aws.amazon.com/firehose/)
- [Amazon Data Firehose — Developer Guide](https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html)
- [Kinesis Data Streams vs Data Firehose (FAQ)](https://aws.amazon.com/kinesis/data-firehose/faqs/)

## Management & Governance

### AWS Control Tower

**Concept** — Control Tower is the **automated way to set up and govern a secure,
multi-account AWS environment** — a *landing zone* — based on AWS best practices,
in a few clicks instead of weeks of manual wiring. It doesn't replace the
underlying services; it **orchestrates** them: AWS Organizations (account
structure, Organizational Units (OUs), and Service Control Policies (SCPs)), AWS
Config (records and evaluates resource configuration), CloudFormation/Service
Catalog (Account Factory, which vends standardized new accounts), and IAM
Identity Center (workforce single sign-on (SSO)). It bootstraps a dedicated
**log archive** and **audit** account, applies **guardrails**, and gives you a
dashboard over the whole org.

**Why it matters** — Building a compliant multi-account foundation by hand —
org structure, centralized logging, an audit account, SSO, and a consistent set
of policies — is slow and error-prone. Control Tower automates that initial
landing zone *and* keeps governing it. Its **guardrails** come in two kinds:
**preventive** (SCPs that *stop* disallowed actions) and **detective** (Config
rules that *flag* drift after the fact). **Account Factory** then makes every
new account come out pre-configured and compliant.

**Exam angle — don't confuse with:**

- **vs AWS Organizations** — the key distinction. Organizations is the
  *structure*: accounts, OUs, consolidated billing, and raw SCPs. Control Tower
  is *automated governance on top of* Organizations. Keyword cues: *"quickly
  set up a governed multi-account landing zone with guardrails"* → Control
  Tower; *"just need an account hierarchy / consolidated billing / apply an
  SCP"* → Organizations.
- **vs AWS Config** — Config is the engine for **detective** guardrails (it
  records and evaluates resource state); Control Tower *consumes* Config. Config
  alone isn't multi-account setup or preventive policy.
- **vs Service Catalog** — Control Tower's **Account Factory** is built on
  Service Catalog to provision standardized accounts; Service Catalog by itself
  is approved-product templates, not landing-zone governance.

**Scenario — design:** A company is starting fresh on AWS and wants a
multi-account foundation from day one — separate prod/dev/sandbox OUs,
centralized logging and audit accounts, SSO, and guardrails that stop risky
actions. → **Control Tower**: stand up the landing zone, use **Account Factory**
to vend each new account pre-governed, and enable preventive + detective
guardrails. Plain Organizations would mean wiring all of that by hand.

**Scenario — lift & shift:** An organization already has a dozen accounts in AWS
Organizations created ad hoc, and wants to bring them under consistent
governance without rebuilding. → Adopt **Control Tower** and **enroll** the
existing OUs/accounts into the landing zone, applying guardrails to accounts
that were previously ungoverned (subject to Control Tower's prerequisites).

**Resources:**

- [AWS Control Tower — product page](https://aws.amazon.com/controltower/)
- [What is AWS Control Tower? (User Guide)](https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html)
- [Control Tower controls (guardrails) reference](https://docs.aws.amazon.com/controltower/latest/controlreference/controls.html)

## Developer Tools

### AWS X-Ray

**Concept** — X-Ray is a **distributed tracing** service: it follows a single
request as it travels through all the components of a distributed or serverless
application and stitches the hops together into one **end-to-end trace**. From
those traces it builds a **service map** — a visual graph of how your services
call each other, annotated with latency, error rates, and faults at each node.
You instrument the app (via the X-Ray SDK (Software Development Kit), or
automatically for Lambda and API Gateway), X-Ray **samples** requests to keep
overhead low, and each trace is broken into **segments and subsegments** that
capture timing, metadata, and errors per hop.

**Why it matters** — In a microservices or serverless architecture, one user
request fans out across many services, so when it's slow or failing, metrics and
logs alone can't tell you *which hop* is to blame. X-Ray pinpoints the offending
service or dependency on the request path and surfaces latency bottlenecks and
error hot spots that are otherwise invisible end-to-end. It integrates with
Lambda, API Gateway, ECS, EC2, Elastic Beanstalk, and App Mesh.

**Exam angle — don't confuse with:**

- **vs CloudWatch** — the key pairing. CloudWatch is **metrics, logs, alarms,
  and dashboards** — the *"what and how much"* (CPU high? error count up?). X-Ray
  is **traces and the service map** — the *"where in the request path"*. They're
  complementary: CloudWatch tells you something is wrong; X-Ray tells you which
  service caused it. Keyword cues: *"trace a request across microservices / find
  the latency bottleneck / service map"* → X-Ray; *"metric / alarm / log /
  dashboard"* → CloudWatch.
- **vs CloudTrail** — easy to mix up by name. CloudTrail is an **audit log of
  AWS API calls** (who did what to your account, for governance/compliance).
  X-Ray traces **application requests** for performance and debugging. Audit
  trail → CloudTrail; request trace → X-Ray.

**Scenario — design:** You're building a serverless API — API Gateway → Lambda →
DynamoDB — and users report intermittent slowness you can't reproduce. → Enable
**X-Ray** tracing on API Gateway and Lambda; the service map and trace timeline
show whether the latency is in the function, a downstream call, or DynamoDB,
without adding manual logging to every layer.

**Scenario — lift & shift:** You've decomposed a migrated monolith into
microservices running on ECS and lost the single-process call stack you used to
debug with. → Instrument the services with the **X-Ray SDK** (or pull traces via
the **App Mesh** integration) to regain end-to-end visibility across the new
inter-service calls.

**Resources:**

- [AWS X-Ray — product page](https://aws.amazon.com/xray/)
- [What is AWS X-Ray? (Developer Guide)](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html)
- [X-Ray concepts: traces, segments, service map](https://docs.aws.amazon.com/xray/latest/devguide/xray-concepts.html)

## Machine Learning & AI

### Amazon Textract

**Concept** — Textract is a fully managed service that **automatically extracts
text, handwriting, tables, and form data from scanned documents, PDFs (Portable
Document Format), and images**. It goes beyond plain OCR (Optical Character
Recognition) — instead of returning a flat blob of characters, it **understands
document structure**, pulling out key-value pairs from forms and rows/cells from
tables with confidence scores. No machine-learning experience is needed: you
call an API and get back structured data. Purpose-built operations exist for
common documents — `AnalyzeExpense` (invoices/receipts), `AnalyzeID` (identity
documents), and `Queries` (ask natural-language questions of a document).

**Why it matters** — Digitizing documents by hand is slow and error-prone, and
basic OCR loses the structure that makes the data useful. Textract preserves
relationships — *this label goes with this value*, *this cell belongs to this
column* — so downstream systems can consume the output directly instead of
re-parsing free text. It's the standard first stage of a document-processing
pipeline, frequently feeding its text into Comprehend for further analysis.

**Exam angle — don't confuse with:**

- **vs Amazon Rekognition** — both can "read text," but the input differs.
  Rekognition finds text *in scenes/photos and video* (a street sign, a label)
  alongside object/face detection. Textract extracts text *and structure* from
  *documents, forms, and tables*. Keyword cues: *"scanned documents / invoices /
  forms / tables"* → Textract; *"objects, faces, or text in photos and video"* →
  Rekognition.
- **vs Amazon Comprehend** — these **chain**, they don't compete. Textract
  *extracts* the raw text; Comprehend does NLP (Natural Language Processing) on
  that text — entities, sentiment, key phrases, language. Extraction → Textract;
  understanding/analysis → Comprehend.

**Scenario — design:** You're building a serverless invoice-processing pipeline.
Users upload scanned invoices to S3, and you need vendor, total, and line items
as structured fields. → S3 event → **Lambda** → **Textract `AnalyzeExpense`**
extracts the fields, which you store in DynamoDB (optionally passing free-text
notes to **Comprehend**). No OCR servers to run and structure is preserved.

**Scenario — lift & shift:** A company migrates a document workflow that today
relies on **manual data entry** (or a self-hosted OCR tool) to key form fields
into a database. → Replace that step with **Textract** form/table extraction to
auto-populate the fields, cutting manual keying while keeping the existing
downstream database.

**Resources:**

- [Amazon Textract — product page](https://aws.amazon.com/textract/)
- [What is Amazon Textract? (Developer Guide)](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)
- [Textract — analyzing documents (forms, tables, queries)](https://docs.aws.amazon.com/textract/latest/dg/how-it-works-analyzing.html)
