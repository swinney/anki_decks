#!/usr/bin/env python3
"""OSI layers for AWS Solutions Architects — Anki deck.

Teaches the OSI 7-layer model through the lens an SA actually needs: which AWS
service operates at which layer, and what that layer lets it do (or not do).

Card archetypes (carried as `type::*` tags):
  - overview : one anchor card per layer
  - service  : a single AWS service -> its layer + consequences
  - contrast : close-pair the exam tests (ALB vs NLB, SG vs NACL, ...)
  - scenario : a requirement -> pick the layer/service

Organization is tag-based (single deck): each card is tagged with its OSI
layer(s) (`OSI::L4-Transport`, ...) and its card type (`type::service`, ...).

Build:  python build_deck.py   # writes ../OSI_Layers_AWS.apkg
"""
import os
import html
import hashlib
import genanki

# ---- AWS homepages used in the Services field -----------------------------
DX        = "https://aws.amazon.com/directconnect/"
SNOW      = "https://aws.amazon.com/snow/"
VPC       = "https://aws.amazon.com/vpc/"
TGW       = "https://aws.amazon.com/transit-gateway/"
VPN       = "https://aws.amazon.com/vpn/"
ELB       = "https://aws.amazon.com/elasticloadbalancing/"
GA        = "https://aws.amazon.com/global-accelerator/"
SHIELD    = "https://aws.amazon.com/shield/"
CLOUDFRONT= "https://aws.amazon.com/cloudfront/"
APIGW     = "https://aws.amazon.com/api-gateway/"
ROUTE53   = "https://aws.amazon.com/route53/"
WAF       = "https://aws.amazon.com/waf/"
APPSYNC   = "https://aws.amazon.com/appsync/"
COGNITO   = "https://aws.amazon.com/cognito/"
ACM       = "https://aws.amazon.com/certificate-manager/"

# ---- OSI layer tags --------------------------------------------------------
L1 = "OSI::L1-Physical"
L2 = "OSI::L2-DataLink"
L3 = "OSI::L3-Network"
L4 = "OSI::L4-Transport"
L5 = "OSI::L5-Session"
L6 = "OSI::L6-Presentation"
L7 = "OSI::L7-Application"

# Each card: key, type, layers (tags), prompt, answer, layer (badge), why,
# services [(label, url)], contrast, exam, acronyms.
CARDS = [
    # ===================== OVERVIEW ANCHORS =====================
    dict(key="ov-l1", type="Overview", layers=[L1], layer="Layer 1 — Physical",
         prompt="OSI Layer 1 (Physical): what is its job, what is the PDU, and which AWS offerings touch it?",
         answer="Moves raw bits over a medium (copper, fiber, radio). PDU = bit. In AWS it is almost entirely AWS-managed; your touchpoints are Direct Connect cross-connects, the fiber between AZs/Regions, and Snow devices (physical data transport).",
         why="Everything rides on it, but the SA only chooses it indirectly — Direct Connect port speed, or shipping data with Snow.",
         services=[("Direct Connect", DX), ("Snow Family", SNOW)],
         contrast="L2 adds framing and MAC addressing on top of these raw bits.",
         exam="Rarely tested directly: 'dedicated physical connection' = Direct Connect; 'ship petabytes' = Snow.",
         acronyms="OSI = Open Systems Interconnection; PDU = Protocol Data Unit; AZ = Availability Zone; MAC = Media Access Control; SA = Solutions Architect; AWS = Amazon Web Services."),

    dict(key="ov-l2", type="Overview", layers=[L2], layer="Layer 2 — Data Link",
         prompt="OSI Layer 2 (Data Link): job, PDU, and AWS touchpoints?",
         answer="Frames bits and addresses the local hop via MAC; handles VLAN tagging and per-link error detection. PDU = frame. In AWS: Direct Connect 802.1Q VLANs (virtual interfaces), Link Aggregation Groups, and the virtual Ethernet an ENI presents.",
         why="Defines the local broadcast domain. AWS abstracts most of it, but DX VLANs and LAG are explicit L2 design choices.",
         services=[("Direct Connect", DX)],
         contrast="L2 = MAC on a single hop; L3 = IP routing across many hops.",
         exam="Keywords '802.1Q', 'VLAN', 'LAG', 'MAC' point to L2 / Direct Connect.",
         acronyms="OSI = Open Systems Interconnection; MAC = Media Access Control; VLAN = Virtual Local Area Network; LAG = Link Aggregation Group; ENI = Elastic Network Interface; DX = Direct Connect; VIF = Virtual Interface; IP = Internet Protocol; PDU = Protocol Data Unit."),

    dict(key="ov-l3", type="Overview", layers=[L3], layer="Layer 3 — Network",
         prompt="OSI Layer 3 (Network): job, PDU, and AWS touchpoints?",
         answer="Logical addressing (IP) and routing between networks. PDU = packet. The whole VPC fabric lives here: subnets, route tables, IGW/NAT, NACLs, Site-to-Site VPN (IPsec), Transit Gateway, VPC peering.",
         why="This is where the SA spends the most design effort — addressing, routing, and reachability.",
         services=[("VPC", VPC), ("Transit Gateway", TGW), ("Site-to-Site VPN", VPN)],
         contrast="L3 routes between subnets/networks; L4 manages the end-to-end conversation (ports, TCP state).",
         exam="Keywords 'route table', 'CIDR', 'subnet', 'IPsec', 'NACL' point to L3.",
         acronyms="OSI = Open Systems Interconnection; SA = Solutions Architect; IP = Internet Protocol; VPC = Virtual Private Cloud; IGW = Internet Gateway; NAT = Network Address Translation; NACL = Network Access Control List; VPN = Virtual Private Network; IPsec = Internet Protocol Security; CIDR = Classless Inter-Domain Routing; TCP = Transmission Control Protocol; PDU = Protocol Data Unit."),

    dict(key="ov-l4", type="Overview", layers=[L4], layer="Layer 4 — Transport",
         prompt="OSI Layer 4 (Transport): job, PDU, and AWS touchpoints?",
         answer="End-to-end delivery between processes via ports; reliability/ordering (TCP) or speed (UDP). PDU = segment (TCP) / datagram (UDP). AWS: NLB, Security Groups (stateful, port/protocol), Global Accelerator, Shield (SYN/UDP floods).",
         why="Port- and connection-level decisions: load balancing without reading payload, stateful firewalling, anycast acceleration.",
         services=[("Network Load Balancer", ELB), ("Global Accelerator", GA), ("Shield", SHIELD)],
         contrast="L4 sees only IP:port; L7 reads the actual HTTP request.",
         exam="Keywords 'TCP/UDP', 'port', 'preserve source IP', 'connection scale' point to L4 / NLB.",
         acronyms="OSI = Open Systems Interconnection; TCP = Transmission Control Protocol; UDP = User Datagram Protocol; NLB = Network Load Balancer; SYN = Synchronize (TCP handshake); IP = Internet Protocol; HTTP = HyperText Transfer Protocol; PDU = Protocol Data Unit."),

    dict(key="ov-l5", type="Overview", layers=[L5], layer="Layer 5 — Session",
         prompt="OSI Layer 5 (Session): job, and the (weak) AWS analogs?",
         answer="Establishes, maintains, and tears down conversations between endpoints (dialogue control, checkpoints). Few direct AWS analogs: load-balancer session stickiness, TLS session resumption, and sticky RPC connections approximate it.",
         why="Cloud stacks collapse L5–L7 into 'the application'; treat L5 conceptually rather than as a service you configure.",
         services=[("Elastic Load Balancing", ELB)],
         contrast="Stickiness keeps a user on one target (the session) vs L7 routing which chooses which target.",
         exam="Rarely labeled 'Layer 5'; shows up as 'session affinity / sticky sessions'.",
         acronyms="TLS = Transport Layer Security; RPC = Remote Procedure Call; ELB = Elastic Load Balancing; OSI = Open Systems Interconnection."),

    dict(key="ov-l6", type="Overview", layers=[L6], layer="Layer 6 — Presentation",
         prompt="OSI Layer 6 (Presentation): job and AWS touchpoints?",
         answer="Data translation: encryption/decryption, encoding, and compression — making bytes intelligible to the app. AWS: TLS/SSL termination with ACM certificates, in-transit encryption, CloudFront content compression.",
         why="Where 'encrypt in transit' and 'terminate TLS at the edge / load balancer' decisions live.",
         services=[("Certificate Manager (ACM)", ACM), ("CloudFront", CLOUDFRONT)],
         contrast="L6 = how data is encoded/encrypted; L7 = what the request means.",
         exam="Keywords 'TLS termination', 'ACM cert', 'in-transit encryption', 'gzip/brotli' point to L6.",
         acronyms="OSI = Open Systems Interconnection; TLS = Transport Layer Security; SSL = Secure Sockets Layer; ACM = AWS Certificate Manager; AWS = Amazon Web Services."),

    dict(key="ov-l7", type="Overview", layers=[L7], layer="Layer 7 — Application",
         prompt="OSI Layer 7 (Application): job and AWS touchpoints?",
         answer="The protocols apps speak — HTTP(S), DNS, gRPC, GraphQL. PDU = message/data. AWS: ALB, CloudFront, API Gateway, Route 53 (DNS), WAF, AppSync, Cognito.",
         why="Content-aware decisions: route by URL/host, inspect or block requests, cache, authenticate.",
         services=[("Application Load Balancer", ELB), ("CloudFront", CLOUDFRONT), ("API Gateway", APIGW), ("Route 53", ROUTE53), ("WAF", WAF)],
         contrast="L7 reads the request; L4 only sees IP:port.",
         exam="Keywords 'path/host routing', 'inspect HTTP', 'cache', 'JWT auth' point to L7.",
         acronyms="OSI = Open Systems Interconnection; HTTP = HyperText Transfer Protocol; HTTPS = HTTP Secure; DNS = Domain Name System; gRPC = a high-performance Remote Procedure Call (RPC) framework; GraphQL = Graph Query Language; ALB = Application Load Balancer; WAF = Web Application Firewall; API = Application Programming Interface; JWT = JSON Web Token; IP = Internet Protocol; URL = Uniform Resource Locator; PDU = Protocol Data Unit."),

    # ===================== SERVICE -> LAYER =====================
    dict(key="s-dx", type="Service → Layer", layers=[L1, L2], layer="Layers 1–2 — Physical / Data Link",
         prompt="Direct Connect operates at which layer(s), and why choose it?",
         answer="Layers 1–2. A dedicated private cross-connect into AWS, carved into 802.1Q VLANs (virtual interfaces).",
         why="Consistent bandwidth/latency and lower egress cost vs the public internet — but not encrypted by itself (pair with a VPN for encryption).",
         services=[("Direct Connect", DX)],
         contrast="Site-to-Site VPN = L3, encrypted, over the public internet.",
         exam="'dedicated private connection', 'consistent throughput', 'reduce data transfer cost' → Direct Connect.",
         acronyms="VLAN = Virtual Local Area Network; VIF = Virtual Interface; VPN = Virtual Private Network; AWS = Amazon Web Services."),

    dict(key="s-snow", type="Service → Layer", layers=[L1], layer="Layer 1 — Physical",
         prompt="Where do AWS Snow devices sit in the OSI model, and when are they the answer?",
         answer="Effectively Layer 1 (Physical) data transport — 'sneakernet'. You physically ship the data instead of pushing it over a network.",
         why="When the dataset is so large that even a fast link would take weeks, physical transport wins.",
         services=[("Snow Family", SNOW)],
         contrast="DataSync / Direct Connect move data over the wire; Snow moves it by truck/box.",
         exam="'petabytes', 'limited bandwidth', 'ship it' → Snow Family.",
         acronyms="OSI = Open Systems Interconnection; AWS = Amazon Web Services."),

    dict(key="s-vpc", type="Service → Layer", layers=[L3], layer="Layer 3 — Network",
         prompt="VPC subnets and route tables operate at which layer, and what do they control?",
         answer="Layer 3 (Network). Subnets carve the VPC CIDR into routable segments; route tables decide next hops (local, IGW, NAT, TGW, peering).",
         why="Reachability and isolation are fundamentally L3 routing decisions.",
         services=[("VPC", VPC)],
         contrast="Routing (L3) decides the path; Security Groups (L4) decide which ports are allowed.",
         exam="'route table', 'CIDR block', 'public vs private subnet' → L3.",
         acronyms="VPC = Virtual Private Cloud; CIDR = Classless Inter-Domain Routing; IGW = Internet Gateway; NAT = Network Address Translation; TGW = Transit Gateway."),

    dict(key="s-nacl", type="Service → Layer", layers=[L3, L4], layer="Layers 3–4 — Network / Transport",
         prompt="Network ACLs operate at which layer, and what is their defining behavior?",
         answer="Layers 3–4, at the subnet boundary. Stateless: you must allow both directions. Numbered allow AND deny rules, evaluated in order.",
         why="A coarse subnet-wide guard rail; useful for explicit denies (e.g., block an IP range) that Security Groups cannot express.",
         services=[("VPC", VPC)],
         contrast="Security Group = stateful, instance-level, allow-only.",
         exam="'explicit deny', 'subnet-level', 'stateless' → NACL.",
         acronyms="NACL / ACL = Network Access Control List; IP = Internet Protocol; SG = Security Group; VPC = Virtual Private Cloud."),

    dict(key="s-sg", type="Service → Layer", layers=[L4], layer="Layer 4 — Transport",
         prompt="Security Groups operate at which layer, and what is their defining behavior?",
         answer="Layer 4 (Transport), at the instance/ENI. Stateful: return traffic is auto-allowed. Allow-rules only.",
         why="Protocol + port + source/dest control attached to the resource; statefulness means you only open one direction.",
         services=[("VPC", VPC)],
         contrast="NACL = stateless, subnet-level, allow+deny (L3/4).",
         exam="'return traffic automatically allowed', 'instance-level firewall' → Security Group.",
         acronyms="ENI = Elastic Network Interface; NACL = Network Access Control List; VPC = Virtual Private Cloud."),

    dict(key="s-vpn", type="Service → Layer", layers=[L3], layer="Layer 3 — Network",
         prompt="Site-to-Site VPN operates at which layer, and how does it secure traffic?",
         answer="Layer 3 (Network). IPsec tunnels encrypt IP packets over the public internet between your network and a VPC.",
         why="Quick, cheap, encrypted connectivity; throughput and latency vary with the internet (unlike Direct Connect's dedicated link).",
         services=[("Site-to-Site VPN", VPN), ("Transit Gateway", TGW)],
         contrast="Direct Connect = L1/2 dedicated, private, consistent — but no built-in encryption.",
         exam="'encrypted tunnel over the internet to the VPC' → Site-to-Site VPN.",
         acronyms="VPN = Virtual Private Network; IPsec = Internet Protocol Security; IP = Internet Protocol; VPC = Virtual Private Cloud."),

    dict(key="s-tgw", type="Service → Layer", layers=[L3], layer="Layer 3 — Network",
         prompt="Transit Gateway operates at which layer, and what problem does it solve?",
         answer="Layer 3 (Network). A regional hub that routes between many VPCs and on-prem links, replacing a mesh of peering connections.",
         why="Centralizes routing at scale; its route tables decide which attachments can reach which.",
         services=[("Transit Gateway", TGW), ("VPC", VPC)],
         contrast="VPC Peering = 1:1, non-transitive; TGW = hub-and-spoke, transitive routing.",
         exam="'connect hundreds of VPCs', 'transitive routing', 'central hub' → Transit Gateway.",
         acronyms="TGW = Transit Gateway; VPC = Virtual Private Cloud."),

    dict(key="s-gwlb", type="Service → Layer", layers=[L3], layer="Layer 3 — Network",
         prompt="A Gateway Load Balancer (GWLB) operates at which layer, and what is it for?",
         answer="Layer 3 (Network). A transparent 'bump-in-the-wire' that steers packets to a fleet of virtual appliances (firewalls, IDS/IPS) using GENEVE encapsulation on port 6081.",
         why="Lets you insert third-party security appliances inline, scaled and load-balanced, without rewriting per-instance routing.",
         services=[("Gateway Load Balancer", ELB)],
         contrast="ALB = L7 content, NLB = L4 ports, GWLB = L3 packet steering to appliances.",
         exam="'inline third-party firewall / IDS appliances at scale' → GWLB.",
         acronyms="GWLB = Gateway Load Balancer; GENEVE = Generic Network Virtualization Encapsulation; IDS = Intrusion Detection System; IPS = Intrusion Prevention System; ALB = Application Load Balancer; NLB = Network Load Balancer."),

    dict(key="s-nlb", type="Service → Layer", layers=[L4], layer="Layer 4 — Transport",
         prompt="An NLB operates at which OSI layer — and what does that let it do (and not do)?",
         answer="Layer 4 (Transport). Sees only TCP/UDP + IP:port.",
         why="Ultra-low latency, millions of connections, preserves client source IP, one static IP per AZ, handles non-HTTP protocols. Cannot read URLs/headers → no content-based routing.",
         services=[("Network Load Balancer", ELB)],
         contrast="ALB (L7) for path/host routing; GWLB (L3) for inline appliances.",
         exam="'preserve source IP', 'static IP', 'TCP passthrough', 'extreme connections' → NLB.",
         acronyms="OSI = Open Systems Interconnection; NLB = Network Load Balancer; TCP = Transmission Control Protocol; UDP = User Datagram Protocol; HTTP = HyperText Transfer Protocol; IP = Internet Protocol; AZ = Availability Zone; ALB = Application Load Balancer; GWLB = Gateway Load Balancer."),

    dict(key="s-ga", type="Service → Layer", layers=[L4], layer="Layer 4 — Transport",
         prompt="Global Accelerator operates at which layer, and what does it give you?",
         answer="Layer 4 (Transport). Two static anycast IPs at the edge that send TCP/UDP traffic over the AWS backbone to the nearest healthy endpoint.",
         why="Improves latency and availability for TCP/UDP and non-HTTP apps; fast regional failover; fixed entry IPs.",
         services=[("Global Accelerator", GA)],
         contrast="CloudFront = L7, caches HTTP content; Global Accelerator = L4, accelerates connections (no caching).",
         exam="'static anycast IPs', 'TCP/UDP', 'global failover', 'gaming/VoIP' → Global Accelerator.",
         acronyms="IP = Internet Protocol; TCP = Transmission Control Protocol; UDP = User Datagram Protocol; HTTP = HyperText Transfer Protocol; VoIP = Voice over IP."),

    dict(key="s-shield", type="Service → Layer", layers=[L3, L4], layer="Layers 3–4 — Network / Transport",
         prompt="AWS Shield protects at which layer(s), and against what?",
         answer="Layers 3–4. Shield (Standard/Advanced) absorbs volumetric and state-exhaustion DDoS — SYN/UDP floods, reflection attacks.",
         why="Network/transport-layer attack mitigation; pair with WAF for L7 attacks.",
         services=[("Shield", SHIELD), ("WAF", WAF)],
         contrast="Shield = L3/4 DDoS volume; WAF = L7 request filtering (SQLi, XSS, bots).",
         exam="'volumetric DDoS', 'SYN flood' → Shield; 'malicious HTTP requests' → WAF.",
         acronyms="DDoS = Distributed Denial of Service; SYN = Synchronize (TCP); UDP = User Datagram Protocol; WAF = Web Application Firewall; SQLi = SQL Injection; XSS = Cross-Site Scripting; HTTP = HyperText Transfer Protocol."),

    dict(key="s-stickiness", type="Service → Layer", layers=[L5], layer="Layer 5 — Session",
         prompt="Where does load-balancer 'session stickiness' map in the OSI model, and what does it do?",
         answer="Closest to Layer 5 (Session). Stickiness binds a client's session to one target (a cookie on ALB, or source-IP/flow on NLB) so stateful sessions stay consistent.",
         why="Keeps session state coherent when the app is not fully stateless; OSI L5 manages the conversation.",
         services=[("Elastic Load Balancing", ELB)],
         contrast="L7 routing decides which target by content; stickiness (L5) keeps you on that target.",
         exam="'maintain user session on same instance', 'sticky sessions' → session affinity.",
         acronyms="ALB = Application Load Balancer; NLB = Network Load Balancer; IP = Internet Protocol; ELB = Elastic Load Balancing; OSI = Open Systems Interconnection."),

    dict(key="s-acm", type="Service → Layer", layers=[L6], layer="Layer 6 — Presentation",
         prompt="ACM and TLS termination relate to which layer, and why?",
         answer="Layer 6 (Presentation). TLS encrypts/decrypts and negotiates how data is represented on the wire; ACM provisions and auto-renews the certificates used to terminate TLS on ALB, CloudFront, and API Gateway.",
         why="Encryption/encoding is presentation-layer work; ACM removes the manual cert toil.",
         services=[("Certificate Manager (ACM)", ACM), ("CloudFront", CLOUDFRONT)],
         contrast="L6 = how data is secured/encoded; L7 = what the request means.",
         exam="'free auto-renewing TLS certs', 'terminate HTTPS at the LB/edge' → ACM.",
         acronyms="ACM = AWS Certificate Manager; TLS = Transport Layer Security; HTTPS = HTTP Secure; ALB = Application Load Balancer; LB = Load Balancer; API = Application Programming Interface."),

    dict(key="s-alb", type="Service → Layer", layers=[L7], layer="Layer 7 — Application",
         prompt="An ALB operates at which OSI layer — and what does that enable?",
         answer="Layer 7 (Application). Reads HTTP/HTTPS.",
         why="Path- and host-based routing, header/cookie/query routing, TLS termination, native HTTP/2 and WebSocket, a target group per microservice, redirects/fixed responses, and auth via Cognito/OIDC.",
         services=[("Application Load Balancer", ELB), ("Cognito", COGNITO)],
         contrast="NLB (L4) when you need raw TCP/UDP, source-IP preservation, or non-HTTP.",
         exam="'route by URL path/host', 'microservices', 'HTTP header routing' → ALB.",
         acronyms="OSI = Open Systems Interconnection; ALB = Application Load Balancer; HTTP = HyperText Transfer Protocol; HTTPS = HTTP Secure; TLS = Transport Layer Security; OIDC = OpenID Connect; NLB = Network Load Balancer; TCP = Transmission Control Protocol; UDP = User Datagram Protocol; IP = Internet Protocol; URL = Uniform Resource Locator."),

    dict(key="s-cloudfront", type="Service → Layer", layers=[L7], layer="Layer 7 — Application",
         prompt="CloudFront operates at which layer, and what does it do?",
         answer="Layer 7 (Application). A CDN that caches and serves HTTP(S) content from edge locations near users; can run logic via Lambda@Edge / CloudFront Functions.",
         why="Lowers latency for content, offloads origins, terminates TLS at the edge, and integrates WAF/Shield.",
         services=[("CloudFront", CLOUDFRONT), ("WAF", WAF)],
         contrast="Global Accelerator = L4 connection acceleration with no caching.",
         exam="'cache static/dynamic content at edge', 'reduce origin load' → CloudFront.",
         acronyms="CDN = Content Delivery Network; HTTP = HyperText Transfer Protocol; HTTPS = HTTP Secure; TLS = Transport Layer Security; WAF = Web Application Firewall."),

    dict(key="s-apigw", type="Service → Layer", layers=[L7], layer="Layer 7 — Application",
         prompt="API Gateway operates at which layer, and what does it manage?",
         answer="Layer 7 (Application). Fronts HTTP/REST/WebSocket APIs: routing, throttling, authorization, request/response transformation, and caching.",
         why="A managed front door for APIs and serverless backends; handles L7 concerns so Lambda does not have to.",
         services=[("API Gateway", APIGW), ("Cognito", COGNITO)],
         contrast="ALB also does L7 HTTP routing, but API Gateway adds API-specific features (keys, usage plans, transforms).",
         exam="'managed REST/WebSocket API', 'throttling', 'API keys', 'serverless front door' → API Gateway.",
         acronyms="API = Application Programming Interface; REST = Representational State Transfer; HTTP = HyperText Transfer Protocol; ALB = Application Load Balancer."),

    dict(key="s-route53", type="Service → Layer", layers=[L7], layer="Layer 7 — Application",
         prompt="Route 53 operates at which layer, and what makes DNS an L7 service?",
         answer="Layer 7 (Application) — DNS is an application-layer protocol. Route 53 resolves names to addresses and steers traffic via routing policies (latency, geo, weighted, failover) with health checks.",
         why="Traffic management and global failover happen at name-resolution time, before a connection is even made.",
         services=[("Route 53", ROUTE53)],
         contrast="ALB host routing picks a target within a region; Route 53 picks which endpoint/region entirely.",
         exam="'latency-based routing', 'weighted', 'failover DNS', 'geolocation' → Route 53.",
         acronyms="DNS = Domain Name System; ALB = Application Load Balancer."),

    dict(key="s-waf", type="Service → Layer", layers=[L7], layer="Layer 7 — Application",
         prompt="AWS WAF operates at which layer, and what does it inspect?",
         answer="Layer 7 (Application). Inspects HTTP(S) requests and blocks by rules — SQL injection, XSS, bad bots, rate limits, geo — on CloudFront, ALB, API Gateway, or AppSync.",
         why="Application-layer threats require inspecting request content, which only L7 sees.",
         services=[("WAF", WAF), ("CloudFront", CLOUDFRONT), ("Application Load Balancer", ELB)],
         contrast="Shield = L3/4 DDoS volume; WAF = L7 request content.",
         exam="'block SQLi/XSS', 'rate-limit by IP', 'filter HTTP requests' → WAF.",
         acronyms="WAF = Web Application Firewall; HTTP = HyperText Transfer Protocol; SQL = Structured Query Language; SQLi = SQL Injection; XSS = Cross-Site Scripting; ALB = Application Load Balancer; API = Application Programming Interface; IP = Internet Protocol."),

    dict(key="s-appsync", type="Service → Layer", layers=[L7], layer="Layer 7 — Application",
         prompt="AppSync operates at which layer, and what protocol does it serve?",
         answer="Layer 7 (Application). A managed GraphQL endpoint (with real-time subscriptions over WebSocket) in front of data sources like DynamoDB, Lambda, and RDS.",
         why="Lets clients fetch exactly the data they need in one request; supports real-time and offline sync.",
         services=[("AppSync", APPSYNC)],
         contrast="API Gateway = REST/HTTP/WebSocket; AppSync = GraphQL specifically.",
         exam="'managed GraphQL API', 'real-time subscriptions', 'mobile offline sync' → AppSync.",
         acronyms="GraphQL = Graph Query Language; REST = Representational State Transfer; HTTP = HyperText Transfer Protocol; API = Application Programming Interface; RDS = Relational Database Service."),

    dict(key="s-cognito", type="Service → Layer", layers=[L7], layer="Layer 7 — Application",
         prompt="Cognito operates at which layer, and what does it handle?",
         answer="Layer 7 (Application). Application identity: user sign-up/sign-in (User Pools) and temporary AWS credentials for app users (Identity Pools), issuing JWT / OIDC tokens.",
         why="Authentication and authorization are application-layer concerns; Cognito integrates with ALB and API Gateway.",
         services=[("Cognito", COGNITO), ("API Gateway", APIGW)],
         contrast="IAM = AWS-account/service identities; Cognito = your app's end-user identities.",
         exam="'sign in app users', 'social/OIDC login', 'JWT to API Gateway' → Cognito.",
         acronyms="JWT = JSON Web Token; OIDC = OpenID Connect; IAM = Identity and Access Management; API = Application Programming Interface; ALB = Application Load Balancer; AWS = Amazon Web Services."),

    # ===================== CONTRAST PAIRS =====================
    dict(key="c-lbs", type="Contrast", layers=[L3, L4, L7], layer="Layers 3 / 4 / 7",
         prompt="ALB vs NLB vs GWLB — which OSI layer and which job?",
         answer="ALB = L7 (HTTP content routing). NLB = L4 (TCP/UDP, IP:port, source-IP preserving, extreme scale). GWLB = L3 (transparent packet steering to inline appliances via GENEVE).",
         why="The layer each one reads determines what it is able to decide on.",
         services=[("Elastic Load Balancing", ELB)],
         contrast="Pick by what you must inspect: URL → ALB, port/IP → NLB, whole packet to an appliance → GWLB.",
         exam="Map the keyword: 'path/host' → ALB; 'source IP / static IP / TCP' → NLB; 'firewall appliance' → GWLB.",
         acronyms="OSI = Open Systems Interconnection; ALB = Application Load Balancer; NLB = Network Load Balancer; GWLB = Gateway Load Balancer; HTTP = HyperText Transfer Protocol; TCP = Transmission Control Protocol; UDP = User Datagram Protocol; IP = Internet Protocol; URL = Uniform Resource Locator; GENEVE = Generic Network Virtualization Encapsulation."),

    dict(key="c-sg-nacl", type="Contrast", layers=[L3, L4], layer="Layers 3–4 — Network / Transport",
         prompt="Security Group vs NACL — layer, state, scope, and rule types?",
         answer="SG: L4, instance/ENI, stateful, allow-only. NACL: L3/4, subnet, stateless, ordered allow+deny.",
         why="Statefulness and scope decide which one you reach for.",
         services=[("VPC", VPC)],
         contrast="Need an explicit deny or a subnet-wide guard → NACL; default instance firewall → SG.",
         exam="'return traffic auto-allowed' → SG; 'block a specific IP range at the subnet' → NACL.",
         acronyms="SG = Security Group; NACL = Network Access Control List; ENI = Elastic Network Interface; IP = Internet Protocol; VPC = Virtual Private Cloud."),

    dict(key="c-waf-shield", type="Contrast", layers=[L3, L4, L7], layer="Layers 3/4 vs 7",
         prompt="WAF vs Shield — which layers, which attacks?",
         answer="WAF = L7, filters malicious HTTP requests (SQLi, XSS, bots, rate limits). Shield = L3/4, absorbs volumetric / state-exhaustion DDoS (SYN/UDP floods).",
         why="Different layers see different attacks; in practice you deploy both.",
         services=[("WAF", WAF), ("Shield", SHIELD)],
         contrast="Request-content problem → WAF; raw-traffic-volume problem → Shield.",
         exam="'SQL injection / bad bots' → WAF; 'massive traffic flood' → Shield.",
         acronyms="WAF = Web Application Firewall; HTTP = HyperText Transfer Protocol; SQLi = SQL Injection; XSS = Cross-Site Scripting; DDoS = Distributed Denial of Service; SYN = Synchronize (TCP); UDP = User Datagram Protocol."),

    dict(key="c-cf-ga", type="Contrast", layers=[L4, L7], layer="Layer 4 vs Layer 7",
         prompt="CloudFront vs Global Accelerator — layer and purpose?",
         answer="CloudFront = L7 CDN: caches HTTP(S) content at edge locations. Global Accelerator = L4: static anycast IPs accelerating TCP/UDP over the AWS backbone (no caching).",
         why="Cache HTTP content vs accelerate arbitrary connections.",
         services=[("CloudFront", CLOUDFRONT), ("Global Accelerator", GA)],
         contrast="Static website/media → CloudFront; gaming/VoIP/non-HTTP with static IPs → Global Accelerator.",
         exam="'cache content' → CloudFront; 'static anycast IPs / TCP-UDP / fast failover' → Global Accelerator.",
         acronyms="CDN = Content Delivery Network; HTTP = HyperText Transfer Protocol; HTTPS = HTTP Secure; IP = Internet Protocol; TCP = Transmission Control Protocol; UDP = User Datagram Protocol; VoIP = Voice over IP."),

    dict(key="c-dx-vpn", type="Contrast", layers=[L1, L2, L3], layer="Layers 1/2 vs Layer 3",
         prompt="Direct Connect vs Site-to-Site VPN — layer and trade-offs?",
         answer="Direct Connect = L1/2, dedicated private link, consistent latency, not encrypted by default. VPN = L3, IPsec-encrypted over the public internet, quick/cheap, variable performance.",
         why="A physical dedicated path vs an encrypted tunnel over the shared internet.",
         services=[("Direct Connect", DX), ("Site-to-Site VPN", VPN)],
         contrast="Combine them: DX for the path + VPN for the encryption.",
         exam="'consistent / dedicated / low-cost egress' → DX; 'encrypted, fast to set up' → VPN.",
         acronyms="DX = Direct Connect; VPN = Virtual Private Network; IPsec = Internet Protocol Security."),

    dict(key="c-igw-nat", type="Contrast", layers=[L3], layer="Layer 3 — Network",
         prompt="Internet Gateway vs NAT Gateway — same layer, different jobs?",
         answer="Both L3. IGW = bidirectional public reachability for a VPC (public IPs work). NAT GW = outbound-only internet for private-subnet instances (no inbound).",
         why="Public exposure vs outbound-only egress.",
         services=[("VPC", VPC)],
         contrast="Public subnet routes to the IGW; a private subnet's egress goes to a NAT GW (which itself sits in a public subnet and uses the IGW).",
         exam="'private instances need patching but no inbound access' → NAT Gateway.",
         acronyms="IGW = Internet Gateway; NAT = Network Address Translation; GW = Gateway; IP = Internet Protocol; VPC = Virtual Private Cloud."),

    dict(key="c-peering-tgw", type="Contrast", layers=[L3], layer="Layer 3 — Network",
         prompt="VPC Peering vs Transit Gateway — layer and topology?",
         answer="Both L3. Peering = 1:1, non-transitive connection between two VPCs. Transit Gateway = hub-and-spoke with transitive routing across many VPCs and on-prem.",
         why="Scale and transitivity drive the choice.",
         services=[("VPC", VPC), ("Transit Gateway", TGW)],
         contrast="A few VPCs at lowest cost → peering; many VPCs / transitive routing → TGW.",
         exam="'connect dozens/hundreds of VPCs, transitive' → Transit Gateway.",
         acronyms="VPC = Virtual Private Cloud; TGW = Transit Gateway."),

    # ===================== SCENARIO -> SERVICE =====================
    dict(key="sc-path", type="Scenario → Service", layers=[L7], layer="Layer 7 — Application",
         prompt="You must route HTTPS requests to different target groups based on the URL path (/api vs /img). Which layer and service?",
         answer="Layer 7 → Application Load Balancer (path-based routing rules).",
         why="Only an L7 device can read the URL path.",
         services=[("Application Load Balancer", ELB)],
         contrast="An NLB (L4) cannot see the path.",
         exam="Keyword 'route by URL/path/host' → ALB.",
         acronyms="HTTPS = HTTP Secure; HTTP = HyperText Transfer Protocol; URL = Uniform Resource Locator; ALB = Application Load Balancer; NLB = Network Load Balancer."),

    dict(key="sc-sourceip", type="Scenario → Service", layers=[L4], layer="Layer 4 — Transport",
         prompt="A TCP service must see the real client source IP and handle millions of connections with ultra-low latency. Layer and service?",
         answer="Layer 4 → Network Load Balancer.",
         why="NLB preserves source IP and scales at L4 without inspecting the payload.",
         services=[("Network Load Balancer", ELB)],
         contrast="An ALB terminates the connection and would obscure the source IP (it adds X-Forwarded-For instead).",
         exam="'preserve source IP' + 'TCP' + 'scale' → NLB.",
         acronyms="TCP = Transmission Control Protocol; IP = Internet Protocol; NLB = Network Load Balancer; ALB = Application Load Balancer."),

    dict(key="sc-sqli", type="Scenario → Service", layers=[L7], layer="Layer 7 — Application",
         prompt="You need to block SQL-injection and XSS in incoming HTTP requests to a public app. Layer and service?",
         answer="Layer 7 → AWS WAF (attached to CloudFront, ALB, or API Gateway).",
         why="Detecting SQLi/XSS requires inspecting request content, which only L7 sees.",
         services=[("WAF", WAF)],
         contrast="Shield (L3/4) would not see the request payload.",
         exam="'SQL injection / XSS / bad bots' → WAF.",
         acronyms="SQL = Structured Query Language; SQLi = SQL Injection; XSS = Cross-Site Scripting; HTTP = HyperText Transfer Protocol; WAF = Web Application Firewall; ALB = Application Load Balancer; API = Application Programming Interface."),

    dict(key="sc-ddos", type="Scenario → Service", layers=[L3, L4], layer="Layers 3–4 — Network / Transport",
         prompt="Your app faces a massive volumetric UDP/SYN flood. Layer and service?",
         answer="Layers 3–4 → AWS Shield (Advanced for larger attacks plus cost protection).",
         why="Volumetric floods are network/transport-layer and are mitigated by absorption, not request filtering.",
         services=[("Shield", SHIELD)],
         contrast="WAF (L7) handles malicious requests, not raw flood volume.",
         exam="'volumetric DDoS / SYN flood' → Shield.",
         acronyms="UDP = User Datagram Protocol; SYN = Synchronize (TCP); DDoS = Distributed Denial of Service; WAF = Web Application Firewall."),

    dict(key="sc-anycast", type="Scenario → Service", layers=[L4], layer="Layer 4 — Transport",
         prompt="A global TCP/UDP app needs two static entry IPs and fast cross-region failover over the AWS backbone. Layer and service?",
         answer="Layer 4 → Global Accelerator.",
         why="GA provides static anycast IPs and routes connections over the backbone with quick failover; it works for non-HTTP traffic.",
         services=[("Global Accelerator", GA)],
         contrast="CloudFront (L7) is for caching HTTP content, not arbitrary TCP/UDP.",
         exam="'static anycast IPs' + 'TCP/UDP' + 'global failover' → Global Accelerator.",
         acronyms="TCP = Transmission Control Protocol; UDP = User Datagram Protocol; IP = Internet Protocol; HTTP = HyperText Transfer Protocol; GA = Global Accelerator."),

    dict(key="sc-cache", type="Scenario → Service", layers=[L7], layer="Layer 7 — Application",
         prompt="You want to cache static assets close to users worldwide and offload the origin. Layer and service?",
         answer="Layer 7 → CloudFront (CDN).",
         why="Caching HTTP content at edge locations is L7 work.",
         services=[("CloudFront", CLOUDFRONT)],
         contrast="Global Accelerator accelerates connections but does not cache.",
         exam="'cache at edge / reduce origin load / lower content latency' → CloudFront.",
         acronyms="CDN = Content Delivery Network; HTTP = HyperText Transfer Protocol."),

    dict(key="sc-dedicated", type="Scenario → Service", layers=[L1, L2], layer="Layers 1–2 — Physical / Data Link",
         prompt="You need a dedicated, private, consistent-throughput connection from a data center to AWS (and lower egress cost). Layer and service?",
         answer="Layers 1–2 → Direct Connect.",
         why="A physical dedicated link gives the consistent performance the public internet cannot guarantee.",
         services=[("Direct Connect", DX)],
         contrast="A VPN (L3) is encrypted but rides the variable public internet.",
         exam="'dedicated / consistent / private / reduce transfer cost' → Direct Connect.",
         acronyms="AWS = Amazon Web Services; VPN = Virtual Private Network."),

    dict(key="sc-encrypt", type="Scenario → Service", layers=[L3], layer="Layer 3 — Network",
         prompt="You need an encrypted connection from on-prem to a VPC quickly and cheaply, tolerating internet-variable performance. Layer and service?",
         answer="Layer 3 → Site-to-Site VPN (IPsec).",
         why="IPsec encrypts IP packets over the public internet and is fast to stand up.",
         services=[("Site-to-Site VPN", VPN)],
         contrast="Direct Connect (L1/2) is dedicated/consistent but not encrypted by itself and slower to provision.",
         exam="'encrypted tunnel, quick setup, over the internet' → Site-to-Site VPN.",
         acronyms="VPC = Virtual Private Cloud; IPsec = Internet Protocol Security; IP = Internet Protocol; VPN = Virtual Private Network."),

    dict(key="sc-deny", type="Scenario → Service", layers=[L3, L4], layer="Layers 3–4 — Network / Transport",
         prompt="You must block a specific malicious IP range at the subnet boundary, regardless of which instance. Layer and service?",
         answer="Layers 3–4 → Network ACL (explicit deny rule).",
         why="NACLs are subnet-wide and support deny rules; Security Groups cannot deny.",
         services=[("VPC", VPC)],
         contrast="A Security Group is instance-level, allow-only, and stateful.",
         exam="'explicit deny / subnet-level block' → NACL.",
         acronyms="IP = Internet Protocol; NACL = Network Access Control List; SG = Security Group; VPC = Virtual Private Cloud."),
]

TYPE_TAG = {
    "Overview": "type::overview",
    "Service → Layer": "type::service",
    "Contrast": "type::contrast",
    "Scenario → Service": "type::scenario",
}

# Cards whose service/concept is in the HBS interview stack (see the
# hbs-interview-stack memory). Tagged `stack::hbs` so the user can build an Anki
# filtered deck (tag:stack::hbs) for focused interview study. Excludes services
# HBS did not list (Direct Connect, Snow, VPN, Transit Gateway, Global
# Accelerator, CloudFront, WAF-standalone, AppSync, GWLB-standalone).
HBS_KEYS = {
    "ov-l3", "ov-l4", "ov-l5", "ov-l6", "ov-l7",
    "s-vpc", "s-nacl", "s-sg", "s-nlb", "s-shield", "s-stickiness",
    "s-acm", "s-alb", "s-apigw", "s-route53", "s-cognito",
    "c-lbs", "c-sg-nacl", "c-waf-shield", "c-igw-nat",
    "sc-path", "sc-sourceip", "sc-ddos", "sc-deny",
}


def esc(s):
    return html.escape(s)


def stable_guid(key):
    # Deterministic per-card GUID (from the short stable key, not the prompt
    # wording) so rewording a card still updates the same note on re-import.
    return "osicard-" + hashlib.md5(key.encode()).hexdigest()[:12]


def services_html(services):
    return " &middot; ".join(
        f'<a href="{url}">{esc(label)} <span class="ext">&#8599;</span></a>'
        for label, url in services
    )


model = genanki.Model(
    1980150001,
    "OSI Layer Card",
    fields=[
        {"name": "Type"},
        {"name": "Prompt"},
        {"name": "Answer"},
        {"name": "Layer"},
        {"name": "Why"},
        {"name": "Services"},
        {"name": "Contrast"},
        {"name": "ExamAngle"},
        {"name": "Acronyms"},
    ],
    templates=[{
        "name": "Card 1",
        "qfmt": '<div class="type">{{Type}}</div>'
                '<div class="prompt">{{Prompt}}</div>',
        "afmt": '''{{FrontSide}}<hr id="answer">
<div class="layer">{{Layer}}</div>
<div class="answer">{{Answer}}</div>
{{#Why}}<div class="row why"><span class="lab">Why this layer</span>{{Why}}</div>{{/Why}}
{{#Services}}<div class="row svc"><span class="lab">AWS services</span><div class="links">{{Services}}</div></div>{{/Services}}
{{#Contrast}}<div class="row confuse"><span class="lab">Don&#39;t confuse with</span>{{Contrast}}</div>{{/Contrast}}
{{#ExamAngle}}<div class="row exam"><span class="lab">Exam angle</span>{{ExamAngle}}</div>{{/ExamAngle}}
{{#Acronyms}}<div class="acro-label">Acronyms</div><div class="acro">{{Acronyms}}</div>{{/Acronyms}}''',
    }],
    css='''.card { font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 17px; text-align: center; color: #232f3e; background: #fff; padding: 16px; }
.type { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #ec7211; font-weight: 700; }
.prompt { font-size: 20px; font-weight: 600; line-height: 1.4; margin: 8px auto; max-width: 600px; }
.layer { display: inline-block; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #fff; background: #378add; border-radius: 4px; padding: 3px 10px; margin-bottom: 10px; }
.answer { font-size: 17px; line-height: 1.5; margin: 4px auto 12px; max-width: 600px; text-align: left; font-weight: 600; }
.row { text-align: left; max-width: 600px; margin: 10px auto; font-size: 15px; line-height: 1.45; border-left: 3px solid #d5dbdb; padding: 4px 0 4px 12px; }
.row .lab { display: block; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #687078; margin-bottom: 2px; }
.row.why { border-left-color: #687078; }
.row.svc { border-left-color: #0073bb; }
.row.confuse { border-left-color: #d85a30; }
.row.exam { border-left-color: #1d9e75; }
.links a { color: #0073bb; text-decoration: none; }
.links a:hover { text-decoration: underline; }
.ext { font-size: 12px; vertical-align: 1px; }
.acro-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #aab1b8; margin-top: 18px; }
.acro { font-size: 12px; line-height: 1.5; color: #98a0a8; margin: 4px auto 0; max-width: 600px; text-align: left; }
hr#answer { border: none; border-top: 1px solid #d5dbdb; margin: 14px 0; }''',
)

deck = genanki.Deck(1980150002, "OSI Layers for AWS Solutions Architects")


def main():
    keys = [c["key"] for c in CARDS]
    dupes = {k for k in keys if keys.count(k) > 1}
    if dupes:
        raise SystemExit(f"Duplicate card keys: {sorted(dupes)}")

    for c in CARDS:
        tags = list(c["layers"]) + [TYPE_TAG[c["type"]]]
        if c["key"] in HBS_KEYS:
            tags.append("stack::hbs")
        note = genanki.Note(
            model=model,
            guid=stable_guid(c["key"]),
            tags=tags,
            fields=[
                esc(c["type"]),
                esc(c["prompt"]),
                esc(c["answer"]),
                esc(c["layer"]),
                esc(c.get("why", "")),
                services_html(c.get("services", [])),
                esc(c.get("contrast", "")),
                esc(c.get("exam", "")),
                esc(c.get("acronyms", "")),
            ],
        )
        deck.add_note(note)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "OSI_Layers_AWS.apkg")
    genanki.Package(deck).write_to_file(out)
    print(f"Wrote {len(CARDS)} cards to {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
