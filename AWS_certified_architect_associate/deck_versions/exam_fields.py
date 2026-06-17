# SAA-C03 exam fields per service: (pick_when, dont_confuse_with, resilience_scope)
EXAM = {
    # ---------------- Compute ----------------
    "EC2": (
        "Need full OS/instance control, long-running or legacy workloads, custom AMIs, or specialized instance types.",
        "vs Lambda: EC2 = always-on servers you manage; Lambda = serverless, short-lived. vs Lightsail: full config vs simplified fixed-price.",
        "AZ-scoped instance. Achieve HA with Auto Scaling + ELB across multiple AZs."),
    "Lambda": (
        "Event-driven, short tasks (≤15 min), no servers to manage, spiky/unpredictable traffic, pay-per-invocation.",
        "vs EC2/Fargate: no infra to manage. vs Step Functions: Lambda runs code; Step Functions orchestrates multiple functions.",
        "Regional, automatically multi-AZ and highly available."),
    "ECS": (
        "Run Docker containers with AWS-native orchestration; simpler than Kubernetes.",
        "vs EKS: ECS = AWS-proprietary, simpler; EKS = standard Kubernetes, portable. vs Fargate: a launch type, not an alternative.",
        "Regional control plane; spread tasks across AZs for HA."),
    "EKS": (
        "You specifically need Kubernetes — portability, existing k8s tooling/ecosystem.",
        "vs ECS: more complex but standard Kubernetes API and portable.",
        "Regional, multi-AZ managed control plane."),
    "Fargate": (
        "Want containers without provisioning/managing EC2 capacity (serverless containers).",
        "vs EC2 launch type: no node management, but less control and can cost more at steady high scale.",
        "Regional; tasks placed across AZs."),
    "ECS Express Mode": (
        "Go from a container image to a live HTTPS URL with minimal config — a production-ready web app/API without hand-wiring ALB, TLS, scaling and networking, while staying ECS/Fargate-native.",
        "vs plain ECS/Fargate: you configure all the surrounding infra yourself. vs App Runner: similar image→URL idea but a separate service; Express Mode keeps you in ECS with ALB consolidation. vs Elastic Beanstalk: EC2-based PaaS.",
        "Regional; Fargate tasks across AZs behind the managed ALB; auto-scales on traffic/utilization."),
    "Elastic Beanstalk": (
        "Deploy a web app fast without managing infra, while still keeping access to the underlying EC2/ASG/RDS.",
        "vs CloudFormation: Beanstalk = PaaS auto-provisioning; CFN = full IaC control. vs App Runner: Beanstalk exposes resources, App Runner fully abstracts.",
        "Provisions Multi-AZ EC2/ASG; HA depends on environment config."),
    "Lightsail": (
        "Simple workload at a predictable low monthly price with minimal AWS knowledge (blogs, small sites, dev/test).",
        "vs EC2: less flexible, bundled fixed pricing.",
        "Single-AZ by default; limited built-in HA."),
    "Batch": (
        "Run large numbers of batch/HPC jobs via queues with dynamically provisioned compute.",
        "vs Step Functions: Batch = bulk compute jobs; SF = workflow orchestration. vs Lambda: long-running/large jobs.",
        "Regional; provisions compute across AZs."),
    "Auto Scaling": (
        "Maintain availability and match EC2 capacity to demand; self-heals by replacing unhealthy instances.",
        "vs ELB: ASG adds/removes instances, ELB distributes traffic to them — used together.",
        "Spans multiple AZs; a core HA mechanism."),
    "Outposts": (
        "Need AWS services running on-premises for low latency or data-residency requirements.",
        "vs Local Zones/Wavelength: Outposts = AWS hardware in your own data center.",
        "Single site; not inherently HA across Regions."),
    "App Runner": (
        "Quickly deploy a containerized web app/API from source or image, fully managed with auto-scaling.",
        "vs Fargate/ECS: far less configuration. vs Beanstalk: more abstracted and container-first.",
        "Regional, managed HA."),
    "ECR": (
        "Store and manage container images privately, tightly integrated with ECS/EKS and IAM.",
        "vs Docker Hub: AWS-native, IAM-integrated, private by default.",
        "Regional; optional cross-Region replication."),

    # ---------------- Storage ----------------
    "S3": (
        "Durable object storage: static assets, data lake, backups, static website hosting.",
        "vs EBS/EFS: S3 = object storage via HTTP API, not a mountable file system. vs Glacier: hot/frequent vs archival.",
        "Regional (11 nines durability across AZs); optional Cross-Region Replication."),
    "S3 Glacier": (
        "Cheap long-term archive, infrequent access, retrieval delay acceptable (compliance, backups).",
        "vs S3 Standard-IA: Glacier = archival with retrieval latency; choose by access frequency and retrieval time needed.",
        "Regional, multi-AZ durability."),
    "EBS": (
        "Persistent block volume for a single EC2 instance (boot volume, database storage).",
        "vs EFS: EBS = single-AZ, one instance (multi-attach limited); EFS = shared, multi-AZ. vs Instance Store: EBS persists.",
        "AZ-locked. Replicate via snapshots (stored in S3) to other AZs/Regions."),
    "EFS": (
        "Shared POSIX/NFS file system mounted by many Linux EC2 instances across AZs; elastic capacity.",
        "vs EBS: shared and multi-AZ. vs FSx: EFS = Linux/NFS; FSx = Windows/Lustre/ONTAP.",
        "Regional, multi-AZ by default."),
    "FSx": (
        "Managed third-party file systems: FSx for Windows (SMB), Lustre (HPC), NetApp ONTAP, OpenZFS.",
        "vs EFS: FSx for Windows = SMB/Active Directory; Lustre = high-performance compute.",
        "Single- or Multi-AZ depending on type (Windows File Server supports Multi-AZ)."),
    "Storage Gateway": (
        "Hybrid: give on-prem apps seamless access to cloud storage (File, Volume, or Tape Gateway).",
        "vs DataSync: Gateway = ongoing hybrid access; DataSync = bulk transfer/migration.",
        "Backed by Regional S3/Glacier durability."),
    "AWS Backup": (
        "Centralized, policy-based backup across many services with compliance and retention rules.",
        "vs manual snapshots: centralized governance, scheduling, cross-account and cross-Region copy.",
        "Regional; supports cross-Region and cross-account copy."),
    "Snowball": (
        "Migrate huge data sets (TB–PB) offline when network transfer is too slow or costly.",
        "vs DataSync: Snowball = physical/offline device; DataSync = online over the network.",
        "Physical transport into a Region."),
    "DataSync": (
        "Automated online transfer between on-prem and AWS (or AWS-to-AWS); recurring scheduled sync.",
        "vs Storage Gateway: one-time/scheduled migration vs persistent access. vs Snowball: online vs offline.",
        "Regional service."),

    # ---------------- Database ----------------
    "RDS": (
        "Managed relational DB (MySQL/PostgreSQL/MariaDB/Oracle/SQL Server) for OLTP; need SQL/ACID.",
        "vs Aurora: Aurora = AWS-built, faster, auto-scaling storage. vs DynamoDB: relational vs NoSQL.",
        "Single-AZ by default; enable Multi-AZ for HA failover. Read replicas for scale (can be cross-Region)."),
    "Aurora": (
        "MySQL/PostgreSQL-compatible with high performance + durability, auto-scaling storage, up to 15 replicas.",
        "vs RDS: higher performance, 6 copies across 3 AZs. vs DynamoDB: relational vs NoSQL.",
        "Regional; 6-way replication across 3 AZs. Global Database for cross-Region DR."),
    "DynamoDB": (
        "Serverless NoSQL key-value/document, single-digit-ms at any scale, predictable high throughput.",
        "vs RDS/Aurora: NoSQL, no joins. vs DAX/ElastiCache: add a cache for microsecond reads.",
        "Regional, multi-AZ automatically. Global Tables for multi-Region active-active."),
    "ElastiCache": (
        "In-memory cache (Redis/Memcached) to offload DB reads, session store, leaderboards.",
        "vs MemoryDB: ElastiCache = cache layer; MemoryDB = durable primary DB. vs DAX: DAX is DynamoDB-specific.",
        "Redis supports Multi-AZ with replicas; Memcached is not durable."),
    "Redshift": (
        "Petabyte data warehouse for OLAP/analytics and complex SQL over structured data.",
        "vs RDS: OLAP vs OLTP. vs Athena: Redshift = provisioned warehouse; Athena = serverless query on S3.",
        "Single-AZ historically (Multi-AZ now available); snapshots to S3 with cross-Region copy."),
    "Neptune": (
        "Graph database for highly connected data and relationships (social, fraud, recommendations).",
        "vs DynamoDB/RDS: purpose-built graph queries (Gremlin/SPARQL).",
        "Regional, multi-AZ with replicas."),
    "DocumentDB": (
        "MongoDB-compatible document database for JSON workloads at scale, fully managed.",
        "vs DynamoDB: MongoDB API compatibility vs proprietary NoSQL.",
        "Regional, multi-AZ replicas."),
    "Keyspaces": (
        "Managed Apache Cassandra-compatible (CQL), serverless wide-column store.",
        "vs DynamoDB: Cassandra API compatibility for lift-and-shift.",
        "Regional, multi-AZ replication."),
    "Timestream": (
        "Time-series data (IoT sensors, app metrics); purpose-built with automatic tiering.",
        "vs DynamoDB: optimized for time-series queries and retention.",
        "Regional, multi-AZ."),
    "QLDB": (
        "Immutable, cryptographically verifiable ledger / audit trail with a single trusted owner.",
        "vs Managed Blockchain: QLDB = central authority; Blockchain = decentralized multi-party.",
        "Regional, multi-AZ."),
    "DMS": (
        "Migrate databases to AWS with minimal downtime; homogeneous or heterogeneous (with SCT).",
        "vs DataSync: DMS = databases; DataSync = files/objects.",
        "Regional; runs on a replication instance (can be Multi-AZ)."),
    "MemoryDB": (
        "Need Redis as a durable primary database — microsecond reads, ms writes, multi-AZ durability.",
        "vs ElastiCache for Redis: MemoryDB = durable primary store; ElastiCache = cache layer.",
        "Regional, multi-AZ transactional log."),

    # ---------------- Networking ----------------
    "VPC": (
        "Isolated virtual network — control subnets, route tables, and security for your resources.",
        "vs Transit Gateway: VPC = the network; TGW connects many VPCs together.",
        "Regional; subnets are AZ-scoped — span AZs for HA."),
    "Route 53": (
        "DNS + domain registration with routing policies (latency, geolocation, failover, weighted) and health checks.",
        "vs CloudFront: DNS routing vs content caching. vs Global Accelerator: DNS-based vs anycast IP.",
        "Global service."),
    "CloudFront": (
        "Cache and deliver content at edge for low latency; static + dynamic, HTTPS, edge DDoS protection.",
        "vs Global Accelerator: CloudFront caches HTTP content; GA = TCP/UDP anycast, no caching. vs S3 alone: adds edge caching.",
        "Global (edge locations)."),
    "ELB": (
        "Distribute traffic: ALB (HTTP/L7 routing), NLB (TCP/L4, ultra-low latency, static IP), GWLB (appliances).",
        "ALB = L7 path/host routing; NLB = L4, static IP, extreme performance; GWLB = third-party security appliances.",
        "Regional; spans multiple AZs."),
    "API Gateway": (
        "Managed front door for REST/HTTP/WebSocket APIs; throttling, auth, caching for serverless backends.",
        "vs AppSync: API GW = REST/HTTP; AppSync = GraphQL. vs ALB: managed API features (keys, throttle, stages).",
        "Regional (or edge-optimized via CloudFront)."),
    "Direct Connect": (
        "Dedicated private, consistent low-latency bandwidth from on-prem to AWS, bypassing the public internet.",
        "vs Site-to-Site VPN: DX = private/consistent (not encrypted by default, slow to provision); VPN = over internet, encrypted, quick.",
        "Connects to a Region via a DX location; pair with VPN for an encrypted, resilient link."),
    "Transit Gateway": (
        "Hub-and-spoke connecting many VPCs + on-prem at scale (replaces a VPC peering mesh).",
        "vs VPC Peering: TGW = scalable transitive hub; peering = 1:1 and non-transitive.",
        "Regional; peer across Regions for global reach."),
    "Global Accelerator": (
        "Improve global app performance/availability via anycast static IPs over the AWS backbone; fast failover, non-HTTP.",
        "vs CloudFront: GA = no caching, TCP/UDP, static anycast IPs; CloudFront = HTTP content caching.",
        "Global; routes to the nearest healthy Regional endpoint."),
    "PrivateLink": (
        "Privately expose or consume a service across VPCs without internet, NAT, or peering (VPC endpoints).",
        "vs VPC Peering/TGW: PrivateLink = service-specific, one-directional; peering = full network connectivity.",
        "Regional; interface endpoints are per-AZ."),
    "VPN": (
        "Encrypted connectivity over the internet: Site-to-Site (on-prem↔VPC) or Client VPN (users↔VPC).",
        "vs Direct Connect: cheaper and quick, encrypted, but variable internet latency.",
        "Regional; deploy across AZs or attach to a Transit Gateway."),
    "App Mesh": (
        "Service mesh for consistent app-level networking, traffic control, and observability across microservices.",
        "vs Cloud Map: App Mesh = traffic routing/proxy (Envoy); Cloud Map = service discovery.",
        "Regional; works with ECS/EKS/EC2."),
    "Cloud Map": (
        "Service discovery — register app resources and resolve them by name as they change dynamically.",
        "vs Route 53: Cloud Map = application/service registry (including non-IP resources); R53 = DNS.",
        "Regional."),

    # ---------------- Security ----------------
    "IAM": (
        "Control authentication/authorization in AWS — users, groups, roles, policies; roles for temporary/cross-service access.",
        "vs IAM Identity Center: IAM = per-account identities/roles; Identity Center = workforce SSO across accounts. vs Cognito: app end-user auth.",
        "Global service."),
    "IAM Identity Center": (
        "Workforce SSO + centralized access to multiple accounts and apps (successor to AWS SSO).",
        "vs IAM: org-wide SSO vs per-account identities. vs Cognito: workforce vs application customers.",
        "Regional identity store serving the whole Organization."),
    "Cognito": (
        "Add sign-up/sign-in to apps; User Pools (authenticate/user directory) + Identity Pools (temporary AWS credentials).",
        "User Pool = authenticate users; Identity Pool = exchange token for AWS credentials. vs IAM: app customers, not AWS staff.",
        "Regional."),
    "KMS": (
        "Create and manage encryption keys; envelope encryption integrated across AWS services.",
        "vs CloudHSM: KMS = shared, managed, easy; CloudHSM = dedicated single-tenant HSM (FIPS 140-2 L3). vs Secrets Manager: keys vs secrets.",
        "Regional (keys are Region-scoped; multi-Region keys optional)."),
    "CloudHSM": (
        "Need a dedicated single-tenant HSM with full key control, FIPS 140-2 Level 3, or custom crypto.",
        "vs KMS: more control and compliance but more operational overhead.",
        "Regional; cluster across AZs for HA."),
    "Secrets Manager": (
        "Store and automatically rotate secrets (DB credentials, API keys) with built-in rotation via Lambda.",
        "vs SSM Parameter Store: Secrets Manager = native rotation, priced per secret; Parameter Store = free tier, no native rotation.",
        "Regional; optional multi-Region replication."),
    "WAF": (
        "Filter L7 web traffic (SQL injection, XSS, rate-limiting, geo-match) on CloudFront/ALB/API Gateway.",
        "vs Shield: WAF = app-layer rules; Shield = DDoS (L3/4). vs Network Firewall: WAF = web app, NF = VPC network.",
        "Regional (or global when attached to CloudFront)."),
    "Shield": (
        "DDoS protection — Standard is free/automatic; Advanced adds enhanced protection, cost protection, and DRT support.",
        "vs WAF: Shield = DDoS mitigation; WAF = custom rules — commonly used together.",
        "Standard global/automatic; Advanced applies to protected resources."),
    "GuardDuty": (
        "Continuous threat detection from logs (VPC Flow, DNS, CloudTrail) — flags anomalous/malicious activity.",
        "vs Inspector: GuardDuty = active threat detection; Inspector = vulnerability scanning. vs Macie: data-focused.",
        "Regional (per Region); aggregate findings via Organizations."),
    "Inspector": (
        "Automated vulnerability scanning of EC2, ECR images, and Lambda (CVEs, network reachability).",
        "vs GuardDuty: vulnerabilities vs active threats.",
        "Regional."),
    "Macie": (
        "Discover and classify sensitive data (PII) in S3 using machine learning.",
        "vs GuardDuty: data privacy/classification vs threat detection.",
        "Regional."),
    "Security Hub": (
        "Single pane aggregating and prioritizing findings across security services; compliance checks (CIS, etc.).",
        "vs GuardDuty/Inspector/Macie: Security Hub aggregates their findings into one place.",
        "Regional; aggregate across Regions/accounts."),
    "ACM": (
        "Provision, manage, and auto-renew SSL/TLS certificates for AWS resources (free public certs).",
        "vs IAM certificate store: ACM integrates with ELB/CloudFront/API Gateway and auto-renews.",
        "Regional (certs for CloudFront must be in us-east-1)."),
    "Firewall Manager": (
        "Centrally manage WAF, Shield, security groups, and Network Firewall rules across all accounts in Organizations.",
        "vs configuring WAF directly: Firewall Manager enforces policy org-wide and on new resources.",
        "Regional; operates across Organization accounts."),
    "Network Firewall": (
        "Stateful managed network firewall/IPS at the VPC level (traffic filtering, domain allowlists).",
        "vs Security Groups/NACLs: managed, stateful, with IPS and central management. vs WAF: network vs web app.",
        "Regional; deploy endpoints per-AZ."),
    "Detective": (
        "Investigate and visualize the root cause of security findings (behavior graph over time).",
        "vs GuardDuty: GuardDuty detects; Detective investigates.",
        "Regional."),

    # ---------------- Management ----------------
    "CloudWatch": (
        "Metrics, logs, alarms, dashboards; trigger Auto Scaling and alerts; monitor performance/operations.",
        "vs CloudTrail: CW = performance metrics/logs; CloudTrail = API/audit. vs X-Ray: metrics vs traces.",
        "Regional."),
    "CloudTrail": (
        "Audit and governance — record API calls and account activity (who did what, when).",
        "vs CloudWatch: audit vs performance. vs Config: CloudTrail = actions/events; Config = resource state/compliance.",
        "Regional; organization trails plus multi-Region and global-service events."),
    "CloudFormation": (
        "Infrastructure as code via declarative templates; repeatable stacks, multi-account/Region with StackSets.",
        "vs CDK: CFN = YAML/JSON; CDK = code that synthesizes CFN. vs Beanstalk: full control vs PaaS.",
        "Regional (StackSets for multi-account/Region)."),
    "Config": (
        "Track resource configuration changes and evaluate compliance against rules over time.",
        "vs CloudTrail: Config = resource state/compliance; CloudTrail = API events.",
        "Regional; aggregate across accounts/Regions."),
    "Systems Manager": (
        "Operational management at scale: patching, Run Command, Session Manager (no SSH), Parameter Store.",
        "vs Secrets Manager: Parameter Store is cheaper but lacks native rotation. vs OpsWorks: agent ops vs Chef/Puppet.",
        "Regional."),
    "Organizations": (
        "Multi-account management: consolidated billing, Service Control Policies (SCPs), grouping via OUs.",
        "vs Control Tower: Organizations = the structure; Control Tower = automated governance on top.",
        "Global management spanning all member accounts."),
    "Control Tower": (
        "Quickly set up a governed, secure multi-account landing zone with guardrails.",
        "vs Organizations: Control Tower automates setup and guardrails using Organizations/Config/SCPs.",
        "Regional home Region + Organization-wide governance."),
    "Trusted Advisor": (
        "Best-practice checks across cost, performance, security, fault tolerance, and service limits.",
        "vs Compute Optimizer: TA = broad best-practice checks; CO = ML-based right-sizing.",
        "Global, account-level (full checks need Business/Enterprise Support)."),
    "Service Catalog": (
        "Curated catalog of approved IT products for self-service provisioning with governance.",
        "vs CloudFormation: Service Catalog adds an approval/governance layer over CFN templates.",
        "Regional; share across the Organization."),
    "CDK": (
        "Define infrastructure as code in a real programming language (TypeScript/Python) with loops, logic, reuse.",
        "vs CloudFormation: CDK synthesizes to CFN and offers higher-level constructs.",
        "Deploys to a Region via CloudFormation."),
    "OpsWorks": (
        "Managed Chef/Puppet for configuration management (legacy; AWS is winding it down).",
        "vs Systems Manager: SSM is AWS-native with agentless options.",
        "Regional."),
    "Cost Explorer": (
        "Visualize and forecast spend/usage trends and identify cost drivers.",
        "vs Budgets: Cost Explorer = analyze/forecast; Budgets = set thresholds and alert.",
        "Global, account-level."),
    "Budgets": (
        "Set cost, usage, RI, or Savings Plan budgets and get alerts when exceeded or forecast to exceed.",
        "vs Cost Explorer: proactive alerting vs retrospective analysis.",
        "Global, account-level."),
    "Compute Optimizer": (
        "ML-based right-sizing recommendations for EC2/ASG/EBS/Lambda to cut cost or improve performance.",
        "vs Trusted Advisor: deeper right-sizing analysis vs broad best-practice checks.",
        "Regional/account."),
    "Resource Access Manager": (
        "Share resources (subnets, Transit Gateway, License Manager) across accounts without duplicating them.",
        "vs cross-account IAM roles: RAM shares the actual resource, not access to act in another account.",
        "Regional; shares within the Organization."),

    # ---------------- Integration ----------------
    "SQS": (
        "Decouple components with a queue; pull-based buffering to absorb spikes. Standard or FIFO.",
        "vs SNS: SQS = pull/queue, consumed once; SNS = push pub/sub fan-out. vs Kinesis: SQS has no replay/stream ordering.",
        "Regional, redundant across AZs."),
    "SNS": (
        "Pub/sub fan-out pushing to many subscribers (Lambda, SQS, HTTP, email/SMS); event notifications.",
        "vs SQS: push fan-out vs pull queue (combine SNS→SQS to fan out). vs EventBridge: SNS = high-throughput simple; EB = routing/filtering.",
        "Regional, multi-AZ."),
    "EventBridge": (
        "Event bus with content filtering from AWS/SaaS/custom sources; schedule (cron); decoupled event-driven apps.",
        "vs SNS: EB = advanced filtering, schema registry, SaaS, lower throughput; SNS = high-throughput fan-out. vs SQS: routing vs buffering.",
        "Regional."),
    "Step Functions": (
        "Orchestrate multi-step workflows / state machines with retries, branching, and parallel steps.",
        "vs SWF: Step Functions is the newer, preferred service. vs Lambda alone: SF orchestrates; it doesn't run the business logic.",
        "Regional."),
    "AppSync": (
        "Managed GraphQL API with real-time subscriptions and offline sync to DynamoDB/Lambda/etc.",
        "vs API Gateway: GraphQL with real-time vs REST/HTTP.",
        "Regional."),
    "MQ": (
        "Managed ActiveMQ/RabbitMQ to migrate existing apps using standard protocols (JMS, AMQP, MQTT, STOMP).",
        "vs SQS/SNS: MQ for lift-and-shift of existing brokers; SQS/SNS for new cloud-native apps.",
        "Regional; Multi-AZ active/standby option."),
    "SWF": (
        "Coordinate tasks involving human or external workers needing long-running state (legacy; prefer Step Functions).",
        "vs Step Functions: SF is the serverless successor for most use cases.",
        "Regional."),

    # ---------------- Analytics ----------------
    "Kinesis": (
        "Real-time streaming ingest/processing (Data Streams) with ordering and replay; clickstreams, logs, IoT.",
        "vs SQS: Kinesis = ordered, multiple consumers, replayable; SQS = simple decoupling, delete-on-consume. vs Firehose: custom real-time vs managed load.",
        "Regional, multi-AZ; throughput via shards."),
    "Athena": (
        "Serverless ad-hoc SQL on data in S3, pay-per-query, no infrastructure (logs, data-lake exploration).",
        "vs Redshift: serverless query-in-place vs provisioned warehouse. vs Glue: Athena queries; Glue does ETL/catalog.",
        "Regional."),
    "Glue": (
        "Serverless ETL + Data Catalog to prepare/transform data and supply schema for Athena/Redshift.",
        "vs EMR: Glue = serverless ETL; EMR = managed Hadoop/Spark clusters. vs DMS: ETL vs DB migration.",
        "Regional."),
    "EMR": (
        "Big-data frameworks (Spark/Hadoop/Hive/Presto) on managed clusters for heavy custom processing.",
        "vs Glue: cluster-based with more control/cost vs serverless ETL. vs Redshift: processing vs warehouse.",
        "Regional; each cluster runs in a single AZ."),
    "QuickSight": (
        "Serverless BI dashboards and visualizations with ML insights; embeddable analytics.",
        "vs Athena/Redshift: QuickSight is the visualization layer over those data sources.",
        "Regional."),
    "OpenSearch": (
        "Search, log analytics, and observability (full-text search, dashboards).",
        "vs CloudWatch Logs: richer search/analytics. vs Athena: real-time search vs SQL on S3.",
        "Regional; multi-AZ across data nodes."),
    "MSK": (
        "Managed Apache Kafka when you specifically need Kafka or its ecosystem compatibility.",
        "vs Kinesis: MSK = Kafka (portable, more ops); Kinesis = AWS-native and simpler.",
        "Regional, multi-AZ brokers."),
    "Lake Formation": (
        "Build and secure a data lake on S3 with centralized, fine-grained permissions.",
        "vs Glue: Lake Formation adds governance/permissions on top of the Glue catalog.",
        "Regional."),
    "Data Firehose": (
        "Easiest way to load streaming data into S3/Redshift/OpenSearch/Splunk — near real-time, no code, with buffering/transform.",
        "vs Kinesis Data Streams: Firehose = managed delivery to destinations (no consumers/replay); Streams = custom real-time + replay.",
        "Regional, multi-AZ."),

    # ---------------- Developer ----------------
    "CodePipeline": (
        "Orchestrate CI/CD stages (source → build → test → deploy) automatically on each commit.",
        "vs CodeBuild/CodeDeploy: Pipeline orchestrates; Build compiles; Deploy ships.",
        "Regional."),
    "CodeBuild": (
        "Managed build/test — compile, run tests, produce artifacts — pay-per-use with no build servers.",
        "vs Jenkins on EC2: fully serverless build with no infra to manage.",
        "Regional."),
    "CodeDeploy": (
        "Automate deployments to EC2/Lambda/ECS/on-prem with strategies (blue/green, canary, rolling).",
        "vs CodePipeline: CodeDeploy is the deploy stage; Pipeline orchestrates the whole flow.",
        "Regional."),
    "CodeCommit": (
        "Private managed Git repositories with IAM-based access (note: closed to new customers).",
        "vs GitHub/Bitbucket: AWS-hosted with IAM authentication.",
        "Regional."),
    "X-Ray": (
        "Distributed tracing — find latency bottlenecks and errors across microservices and serverless apps.",
        "vs CloudWatch: traces and service maps vs metrics/logs.",
        "Regional."),

    # ---------------- ML / AI ----------------
    "SageMaker": (
        "Build, train, and deploy a custom ML model end-to-end (you need your own model).",
        "vs pre-trained AI services (Rekognition/Comprehend): build-your-own vs ready APIs. vs Bedrock: custom ML vs foundation models.",
        "Regional; multi-AZ inference endpoints."),
    "Rekognition": (
        "Pre-trained image/video analysis — objects, scenes, faces, moderation, text in images.",
        "vs SageMaker: turnkey API vs custom model. vs Textract: scenes/faces vs document text.",
        "Regional."),
    "Comprehend": (
        "NLP on text — sentiment, entities, key phrases, PII detection, topic modeling.",
        "vs Textract: Comprehend analyzes meaning; Textract extracts the text first. vs Translate: understand vs translate.",
        "Regional."),
    "Textract": (
        "Extract text, tables, and form fields from scanned documents, PDFs, and images (OCR+).",
        "vs Rekognition text detection: Textract = documents/forms/tables; Rekognition = text in scenes. Often feeds Comprehend.",
        "Regional."),
    "Bedrock": (
        "Build generative-AI apps using foundation models via one API — no infrastructure or training.",
        "vs SageMaker: managed foundation models vs building/training your own. vs AI services: generative/LLM vs task-specific.",
        "Regional."),
    "Transcribe": (
        "Speech-to-text — turn audio/video into transcripts, call analytics, or captions.",
        "vs Polly: Transcribe = speech→text; Polly = text→speech.",
        "Regional."),
    "Polly": (
        "Text-to-speech with lifelike voices (IVR, accessibility, voice-enabled apps).",
        "vs Transcribe: opposite direction (text→speech).",
        "Regional."),
    "Translate": (
        "Neural machine translation between languages, real-time or batch.",
        "vs Comprehend: translate vs analyze. Often chained Transcribe → Translate → Polly.",
        "Regional."),

    # ---------------- End-user / Other ----------------
    "WorkSpaces": (
        "Persistent managed cloud desktops (DaaS) for employees — a VDI replacement.",
        "vs AppStream 2.0: WorkSpaces = full persistent desktop; AppStream = stream individual apps.",
        "Regional; deploy across AZs."),
    "AppStream 2.0": (
        "Stream specific desktop applications to a browser (non-persistent app delivery).",
        "vs WorkSpaces: single applications vs a full persistent desktop.",
        "Regional, multi-AZ fleets."),
    "SES": (
        "Send and receive bulk or transactional email at scale (notifications, marketing, inbound).",
        "vs SNS: SES = rich/inbound email; SNS = pub/sub including simple email/SMS notifications.",
        "Regional."),
    "Amplify": (
        "Build and host full-stack web and mobile apps fast — frontend hosting plus backend via Cognito/AppSync.",
        "vs Beanstalk: Amplify = frontend/mobile + serverless backend; Beanstalk = server apps. vs App Runner: full-stack/JAMstack vs containers.",
        "Regional; hosting served globally via CDN."),
}
