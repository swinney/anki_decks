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
- [Analytics](#analytics)
  - [Amazon Data Firehose](#amazon-data-firehose)

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
