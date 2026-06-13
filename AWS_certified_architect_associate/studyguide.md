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

- BGP (Border Gateway Protocol) is the routing protocol that powers the internet. Think of it as the internet's postal service or GPS: it evaluates all available network paths and determines the most efficient route for data to travel from one network to another. [1, 2, 3, 4]  
How BGP Works 
The internet is not a single, massive network; it is a collection of thousands of smaller, interconnected networks called Autonomous Systems (AS). These are owned by Internet Service Providers (ISPs), large enterprises, and tech giants. [3, 4, 5]  
When data crosses the globe, it must jump between these different systems. BGP facilitates this by performing three primary tasks: 

• Path Selection: It analyzes all possible routes and chooses the best path based on network rules, policies, and efficiency rather than just the shortest physical distance. 
• Route Advertisement: BGP-enabled routers constantly share (or "advertise") their reachability information, announcing which IP address ranges they can connect to. 
• Policy Control: Network administrators can set BGP policies to prioritize certain routes, avoid congested networks, or balance internet traffic. [8, 9]  

BGP: Internal vs. External 
BGP operates in two distinct ways depending on where the data is traveling: 

• eBGP (External BGP): Used to exchange routing information between different Autonomous Systems (e.g., connecting your ISP's network to a neighboring ISP's network). 
• iBGP (Internal BGP): Used to share routing information within a single Autonomous System (e.g., a massive data center distributing traffic across its own internal servers). [8]  

Why BGP is Essential 
Without BGP, the global internet would not function. It is highly scalable, supports multihoming (allowing an organization to connect to multiple ISPs for redundancy), and automatically updates routing tables if a specific connection fails. [1, 3, 8, 10]  
Because of its foundational role, a misconfigured BGP update can cause massive, global internet outages. To learn more about how internet infrastructure utilizes this protocol, explore Cloudflare's BGP Guide or the Cisco BGP Documentation. [1, 3, 11, 12]  

AI can make mistakes, so double-check responses

[1] https://www.cloudflare.com/learning/security/glossary/what-is-bgp/
[2] https://networklessons.com/bgp
[3] https://community.cisco.com/t5/network-management/what-is-bgp-for-beginners/td-p/5136090
[4] https://aws.amazon.com/what-is/border-gateway-protocol/
[5] https://www.youtube.com/watch?v=A1KXPpqlNZ4
[6] https://www.youtube.com/watch?v=ibK1OpjILk0
[7] https://www.thousandeyes.com/learning/glossary/bgp-border-gateway-protocol
[8] https://www.geeksforgeeks.org/computer-networks/border-gateway-protocol-bgp/
[9] https://www.kentik.com/kentipedia/what-is-bgp-border-gateway-protocol/
[10] https://www.reddit.com/r/selfhosted/comments/1d72t2d/what_does_bgp_do_exactly/
[11] https://www.ntia.gov/programs-and-initiatives/border-gateway-protocol
[12] https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/13754-26.html


