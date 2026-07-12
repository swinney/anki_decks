#!/usr/bin/env python3
"""Build an Anki .apkg deck of exam-relevant AWS services."""
import os
import html
import genanki

# URL map: service name -> AWS product page
URL = {
    # Compute
    "EC2": "https://aws.amazon.com/ec2/",
    "Lambda": "https://aws.amazon.com/lambda/",
    "ECS": "https://aws.amazon.com/ecs/",
    "ECS Express Mode": "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-service-overview.html",
    "EKS": "https://aws.amazon.com/eks/",
    "Fargate": "https://aws.amazon.com/fargate/",
    "Elastic Beanstalk": "https://aws.amazon.com/elasticbeanstalk/",
    "Lightsail": "https://aws.amazon.com/lightsail/",
    "Batch": "https://aws.amazon.com/batch/",
    "Auto Scaling": "https://aws.amazon.com/ec2/autoscaling/",
    "Outposts": "https://aws.amazon.com/outposts/",
    "App Runner": "https://aws.amazon.com/apprunner/",
    "ECR": "https://aws.amazon.com/ecr/",
    # Storage
    "S3": "https://aws.amazon.com/s3/",
    "S3 Glacier": "https://aws.amazon.com/s3/storage-classes/glacier/",
    "EBS": "https://aws.amazon.com/ebs/",
    "EFS": "https://aws.amazon.com/efs/",
    "FSx": "https://aws.amazon.com/fsx/",
    "Storage Gateway": "https://aws.amazon.com/storagegateway/",
    "AWS Backup": "https://aws.amazon.com/backup/",
    "Snowball": "https://aws.amazon.com/snowball/",
    "DataSync": "https://aws.amazon.com/datasync/",
    # Database
    "RDS": "https://aws.amazon.com/rds/",
    "Aurora": "https://aws.amazon.com/rds/aurora/",
    "DynamoDB": "https://aws.amazon.com/dynamodb/",
    "ElastiCache": "https://aws.amazon.com/elasticache/",
    "Redshift": "https://aws.amazon.com/redshift/",
    "Neptune": "https://aws.amazon.com/neptune/",
    "DocumentDB": "https://aws.amazon.com/documentdb/",
    "Keyspaces": "https://aws.amazon.com/keyspaces/",
    "Timestream": "https://aws.amazon.com/timestream/",
    "QLDB": "https://aws.amazon.com/qldb/",
    "DMS": "https://aws.amazon.com/dms/",
    "MemoryDB": "https://aws.amazon.com/memorydb/",
    # Networking & Content Delivery
    "VPC": "https://aws.amazon.com/vpc/",
    "Route 53": "https://aws.amazon.com/route53/",
    "CloudFront": "https://aws.amazon.com/cloudfront/",
    "ELB": "https://aws.amazon.com/elasticloadbalancing/",
    "API Gateway": "https://aws.amazon.com/api-gateway/",
    "Direct Connect": "https://aws.amazon.com/directconnect/",
    "Transit Gateway": "https://aws.amazon.com/transit-gateway/",
    "Global Accelerator": "https://aws.amazon.com/global-accelerator/",
    "PrivateLink": "https://aws.amazon.com/privatelink/",
    "VPN": "https://aws.amazon.com/vpn/",
    "App Mesh": "https://aws.amazon.com/app-mesh/",
    "Cloud Map": "https://aws.amazon.com/cloud-map/",
    # Security, Identity & Compliance
    "IAM": "https://aws.amazon.com/iam/",
    "IAM Identity Center": "https://aws.amazon.com/iam/identity-center/",
    "Cognito": "https://aws.amazon.com/cognito/",
    "KMS": "https://aws.amazon.com/kms/",
    "CloudHSM": "https://aws.amazon.com/cloudhsm/",
    "Secrets Manager": "https://aws.amazon.com/secrets-manager/",
    "WAF": "https://aws.amazon.com/waf/",
    "Shield": "https://aws.amazon.com/shield/",
    "GuardDuty": "https://aws.amazon.com/guardduty/",
    "Inspector": "https://aws.amazon.com/inspector/",
    "Macie": "https://aws.amazon.com/macie/",
    "Security Hub": "https://aws.amazon.com/security-hub/",
    "ACM": "https://aws.amazon.com/certificate-manager/",
    "Firewall Manager": "https://aws.amazon.com/firewall-manager/",
    "Network Firewall": "https://aws.amazon.com/network-firewall/",
    "Detective": "https://aws.amazon.com/detective/",
    # Management & Governance
    "CloudWatch": "https://aws.amazon.com/cloudwatch/",
    "CloudTrail": "https://aws.amazon.com/cloudtrail/",
    "CloudFormation": "https://aws.amazon.com/cloudformation/",
    "Config": "https://aws.amazon.com/config/",
    "Systems Manager": "https://aws.amazon.com/systems-manager/",
    "Organizations": "https://aws.amazon.com/organizations/",
    "Control Tower": "https://aws.amazon.com/controltower/",
    "Trusted Advisor": "https://aws.amazon.com/premiumsupport/technology/trusted-advisor/",
    "Service Catalog": "https://aws.amazon.com/servicecatalog/",
    "CDK": "https://aws.amazon.com/cdk/",
    "OpsWorks": "https://aws.amazon.com/opsworks/",
    "Cost Explorer": "https://aws.amazon.com/aws-cost-management/aws-cost-explorer/",
    "Budgets": "https://aws.amazon.com/aws-cost-management/aws-budgets/",
    "Compute Optimizer": "https://aws.amazon.com/compute-optimizer/",
    "Resource Access Manager": "https://aws.amazon.com/ram/",
    # Application Integration
    "SQS": "https://aws.amazon.com/sqs/",
    "SNS": "https://aws.amazon.com/sns/",
    "EventBridge": "https://aws.amazon.com/eventbridge/",
    "Step Functions": "https://aws.amazon.com/step-functions/",
    "AppSync": "https://aws.amazon.com/appsync/",
    "MQ": "https://aws.amazon.com/amazon-mq/",
    "SWF": "https://aws.amazon.com/swf/",
    # Analytics
    "Kinesis": "https://aws.amazon.com/kinesis/",
    "Athena": "https://aws.amazon.com/athena/",
    "Glue": "https://aws.amazon.com/glue/",
    "EMR": "https://aws.amazon.com/emr/",
    "QuickSight": "https://aws.amazon.com/quicksight/",
    "OpenSearch": "https://aws.amazon.com/opensearch-service/",
    "MSK": "https://aws.amazon.com/msk/",
    "Lake Formation": "https://aws.amazon.com/lake-formation/",
    "Data Firehose": "https://aws.amazon.com/firehose/",
    # Developer / Deployment
    "CodePipeline": "https://aws.amazon.com/codepipeline/",
    "CodeBuild": "https://aws.amazon.com/codebuild/",
    "CodeDeploy": "https://aws.amazon.com/codedeploy/",
    "CodeCommit": "https://aws.amazon.com/codecommit/",
    "X-Ray": "https://aws.amazon.com/xray/",
    # ML / AI
    "SageMaker": "https://aws.amazon.com/sagemaker/",
    "Rekognition": "https://aws.amazon.com/rekognition/",
    "Comprehend": "https://aws.amazon.com/comprehend/",
    "Textract": "https://aws.amazon.com/textract/",
    "Bedrock": "https://aws.amazon.com/bedrock/",
    "Transcribe": "https://aws.amazon.com/transcribe/",
    "Polly": "https://aws.amazon.com/polly/",
    "Translate": "https://aws.amazon.com/translate/",
    # Other
    "WorkSpaces": "https://aws.amazon.com/workspaces/",
    "AppStream 2.0": "https://aws.amazon.com/appstream2/",
    "SES": "https://aws.amazon.com/ses/",
    "Amplify": "https://aws.amazon.com/amplify/",
}

# Each entry: (Name, Category, Description, [associated service names])
SERVICES = [
    ("EC2", "Compute", "Resizable virtual server (instance) capacity in the cloud; the core IaaS building block for running workloads.", ["EBS", "Auto Scaling", "ELB", "VPC", "AMI" if False else "S3"]),
    ("Lambda", "Compute", "Serverless, event-driven compute that runs code without provisioning servers; you pay only for execution time.", ["API Gateway", "EventBridge", "S3", "DynamoDB", "Step Functions"]),
    ("ECS", "Compute", "Fully managed container orchestration service for running Docker containers on EC2 or Fargate.", ["Fargate", "ECR", "EKS", "ELB", "EC2"]),
    ("EKS", "Compute", "Managed Kubernetes control plane for running Kubernetes workloads on AWS without operating your own masters.", ["ECS", "Fargate", "ECR", "EC2", "App Mesh"]),
    ("Fargate", "Compute", "Serverless compute engine for containers that removes the need to provision and manage EC2 instances for ECS/EKS.", ["ECS", "EKS", "ECR"]),
    ("ECS Express Mode", "Compute", "Simplified way to run a containerized web app or API on ECS + Fargate: provide a container image and it auto-provisions the Fargate service, an Application Load Balancer with SSL/TLS, an auto-generated HTTPS domain, auto scaling, monitoring and networking. Supports public or private apps and can consolidate up to 25 Express services behind one ALB. No extra charge beyond the underlying resources.", ["ECS", "Fargate", "ELB", "ACM", "App Runner"]),
    ("Elastic Beanstalk", "Compute", "PaaS that automatically handles deployment, capacity, load balancing and scaling for web apps from uploaded code.", ["EC2", "Auto Scaling", "ELB", "CloudFormation", "RDS"]),
    ("Lightsail", "Compute", "Simplified VPS offering bundled compute, storage and networking at a predictable low price for simple workloads.", ["EC2", "RDS", "Route 53"]),
    ("Batch", "Compute", "Fully managed batch processing that dynamically provisions compute to run large numbers of batch jobs.", ["EC2", "Fargate", "ECS", "Step Functions"]),
    ("Auto Scaling", "Compute", "Automatically adjusts EC2 capacity to maintain performance and minimize cost based on demand or schedules.", ["EC2", "ELB", "CloudWatch"]),
    ("Outposts", "Compute", "Fully managed AWS infrastructure racks delivered on-premises to run AWS services locally with low latency.", ["EC2", "EBS", "S3", "VPC"]),
    ("App Runner", "Compute", "Fully managed service to build and run containerized web apps and APIs directly from source or an image.", ["ECR", "Fargate", "CodePipeline"]),
    ("ECR", "Compute", "Fully managed Docker container registry for storing, managing and deploying container images.", ["ECS", "EKS", "Fargate"]),

    ("S3", "Storage", "Highly durable, scalable object storage for any amount of data, with tiered storage classes and lifecycle policies.", ["S3 Glacier", "CloudFront", "Athena", "Glue", "AWS Backup"]),
    ("S3 Glacier", "Storage", "Low-cost archival object storage classes for long-term, infrequently accessed data with flexible retrieval times.", ["S3", "AWS Backup", "Storage Gateway"]),
    ("EBS", "Storage", "Persistent block storage volumes attached to EC2 instances, with snapshots stored in S3.", ["EC2", "AWS Backup", "S3"]),
    ("EFS", "Storage", "Fully managed elastic NFS file system that can be mounted by many EC2 instances concurrently across AZs.", ["EC2", "Lambda", "FSx", "AWS Backup"]),
    ("FSx", "Storage", "Fully managed third-party file systems (Windows File Server, Lustre, NetApp ONTAP, OpenZFS) for specialized workloads.", ["EFS", "EC2", "S3"]),
    ("Storage Gateway", "Storage", "Hybrid storage service that gives on-premises apps seamless access to cloud storage in S3, Glacier and more.", ["S3", "S3 Glacier", "EBS", "AWS Backup"]),
    ("AWS Backup", "Storage", "Centralized, policy-based backup service to automate and govern backups across AWS services.", ["EBS", "EFS", "RDS", "DynamoDB", "S3"]),
    ("Snowball", "Storage", "Petabyte-scale physical data transport devices for migrating large data sets into and out of AWS.", ["S3", "DataSync", "Storage Gateway"]),
    ("DataSync", "Storage", "Online data transfer service that automates moving data between on-premises storage and AWS storage services.", ["S3", "EFS", "FSx", "Snowball"]),

    ("RDS", "Database", "Managed relational database service supporting engines like MySQL, PostgreSQL, MariaDB, Oracle and SQL Server.", ["Aurora", "DynamoDB", "ElastiCache", "DMS", "AWS Backup"]),
    ("Aurora", "Database", "AWS-built MySQL- and PostgreSQL-compatible relational database with high performance, durability and auto-scaling storage.", ["RDS", "DynamoDB", "ElastiCache", "DMS"]),
    ("DynamoDB", "Database", "Fully managed serverless key-value and document NoSQL database with single-digit-millisecond performance at any scale.", ["Lambda", "DAX" if False else "ElastiCache", "Kinesis", "AWS Backup"]),
    ("ElastiCache", "Database", "Managed in-memory caching service supporting Redis and Memcached to accelerate read-heavy workloads.", ["RDS", "DynamoDB", "MemoryDB"]),
    ("Redshift", "Database", "Petabyte-scale, fully managed cloud data warehouse for fast SQL analytics across structured data.", ["S3", "Glue", "QuickSight", "Athena", "EMR"]),
    ("Neptune", "Database", "Fully managed graph database service supporting property graph and RDF for highly connected data.", ["DynamoDB", "RDS"]),
    ("DocumentDB", "Database", "Fully managed MongoDB-compatible document database designed for JSON workloads at scale.", ["DynamoDB", "RDS"]),
    ("Keyspaces", "Database", "Serverless, fully managed wide-column NoSQL database compatible with Apache Cassandra. You use the same CQL (Cassandra Query Language), drivers, and tools you'd use with Cassandra, but AWS runs it for you — no clusters, nodes, or patching to manage, and it scales tables up and down automatically with pay-per-request or provisioned capacity. Data is replicated across 3 Availability Zones for durability, with single-digit-millisecond performance at scale. Its 'wide-column' model stores rows whose columns can vary, partitioned by a key — ideal for high-volume, write-heavy workloads like time-series, IoT device data, and user activity feeds. Pick it to migrate or build Cassandra workloads without operating the cluster.", ["DynamoDB", "MemoryDB"]),
    ("Timestream", "Database", "Fully managed, purpose-built time-series database for IoT and operational metrics at scale.", ["DynamoDB", "Kinesis"]),
    ("QLDB", "Database", "Fully managed ledger database providing a transparent, immutable, cryptographically verifiable transaction log.", ["DynamoDB"]),
    ("DMS", "Database", "Database Migration Service moves databases and analytics workloads to AWS while the source stays live, keeping downtime to minutes. It runs on a managed replication instance that reads from the source, applies any needed transformation, and writes to the target; with change data capture (CDC) it continuously replicates ongoing changes so source and target stay in sync until you cut over. It handles homogeneous moves (e.g., Oracle→Oracle) and heterogeneous ones (e.g., Oracle→Aurora PostgreSQL) — for heterogeneous, the companion Schema Conversion Tool (SCT) converts schemas and code first. Sources/targets include on-prem and cloud relational engines, plus targets like S3, Redshift, DynamoDB, and Kinesis. Use it to migrate to AWS, replicate across regions/accounts, or feed a data lake — not for ongoing application queries.", ["RDS", "Aurora", "Redshift", "S3"]),
    ("MemoryDB", "Database", "Durable, Redis-compatible in-memory database delivering microsecond reads and single-digit-millisecond writes.", ["ElastiCache", "DynamoDB"]),

    ("VPC", "Networking", "Logically isolated virtual network where you launch AWS resources with full control over IP, subnets and routing.", ["Direct Connect", "Transit Gateway", "PrivateLink", "VPN", "Route 53"]),
    ("Route 53", "Networking", "Highly available and scalable DNS web service with health checks and traffic routing policies.", ["CloudFront", "ELB", "VPC", "Global Accelerator"]),
    ("CloudFront", "Networking", "Global content delivery network (CDN) that caches content at edge locations for low-latency delivery.", ["S3", "Route 53", "WAF", "Global Accelerator", "ACM"]),
    ("ELB", "Networking", "Elastic Load Balancing distributes incoming traffic across targets (ALB, NLB, GLB) for availability and scale.", ["EC2", "Auto Scaling", "ECS", "Route 53"]),
    ("API Gateway", "Networking", "Fully managed service to create, publish and secure REST, HTTP and WebSocket APIs at any scale.", ["Lambda", "Cognito", "WAF", "Step Functions", "AppSync"]),
    ("Direct Connect", "Networking", "Dedicated private network connection from on-premises to AWS for consistent, low-latency bandwidth.", ["VPC", "Transit Gateway", "VPN"]),
    ("Transit Gateway", "Networking", "Central hub that connects VPCs and on-premises networks through a single gateway, simplifying routing.", ["VPC", "Direct Connect", "VPN", "Resource Access Manager"]),
    ("Global Accelerator", "Networking", "Networking service that improves availability and performance using the AWS global network and anycast IPs.", ["CloudFront", "ELB", "Route 53"]),
    ("PrivateLink", "Networking", "Provides private connectivity between VPCs and services without exposing traffic to the public internet.", ["VPC", "Cloud Map", "API Gateway"]),
    ("VPN", "Networking", "Site-to-Site and Client VPN services that establish encrypted tunnels between networks and AWS.", ["VPC", "Direct Connect", "Transit Gateway"]),
    ("App Mesh", "Networking", "Service mesh that provides application-level networking, observability and traffic control across microservices.", ["ECS", "EKS", "Cloud Map", "X-Ray"]),
    ("Cloud Map", "Networking", "Cloud resource discovery service that lets applications find dynamically changing service endpoints.", ["ECS", "App Mesh", "PrivateLink"]),

    ("IAM", "Security", "Identity and Access Management for securely controlling who is authenticated and authorized to use AWS resources.", ["IAM Identity Center", "Organizations", "KMS", "CloudTrail", "Cognito"]),
    ("IAM Identity Center", "Security", "Centrally manage workforce single sign-on and access to multiple AWS accounts and applications.", ["IAM", "Organizations", "Control Tower"]),
    ("Cognito", "Security", "Adds user sign-up, sign-in and access control to web and mobile apps with user pools and identity pools.", ["IAM", "API Gateway", "AppSync", "Amplify"]),
    ("KMS", "Security", "Managed service to create and control encryption keys used to protect data across AWS services.", ["CloudHSM", "Secrets Manager", "S3", "IAM"]),
    ("CloudHSM", "Security", "Dedicated, single-tenant hardware security modules for generating and using your own encryption keys.", ["KMS", "Secrets Manager"]),
    ("Secrets Manager", "Security", "Securely stores, rotates and retrieves credentials, API keys and other secrets.", ["KMS", "RDS", "IAM", "Systems Manager"]),
    ("WAF", "Security", "Web Application Firewall that protects apps from common exploits with customizable rules.", ["CloudFront", "API Gateway", "ELB", "Shield", "Firewall Manager"]),
    ("Shield", "Security", "Managed DDoS protection service; Standard is automatic, Advanced adds enhanced protections and support.", ["WAF", "CloudFront", "Route 53", "Global Accelerator"]),
    ("GuardDuty", "Security", "Intelligent threat detection that continuously monitors for malicious activity and unauthorized behavior.", ["Security Hub", "Detective", "CloudTrail", "Inspector"]),
    ("Inspector", "Security", "Automated vulnerability management that continually scans workloads for software vulnerabilities and exposure.", ["Security Hub", "GuardDuty", "Systems Manager"]),
    ("Macie", "Security", "Uses machine learning to discover, classify and protect sensitive data such as PII stored in S3.", ["S3", "Security Hub", "KMS"]),
    ("Security Hub", "Security", "Centralized security posture management that aggregates and prioritizes findings across AWS security services.", ["GuardDuty", "Inspector", "Macie", "Config", "Detective"]),
    ("ACM", "Security", "AWS Certificate Manager provisions, manages and deploys SSL/TLS certificates for AWS services.", ["CloudFront", "ELB", "API Gateway", "Route 53"]),
    ("Firewall Manager", "Security", "Centrally configure and manage firewall rules (WAF, Shield, security groups) across accounts in Organizations.", ["WAF", "Shield", "Network Firewall", "Organizations"]),
    ("Network Firewall", "Security", "Managed, stateful network firewall and intrusion prevention for VPCs.", ["VPC", "Firewall Manager", "WAF"]),
    ("Detective", "Security", "Analyzes and visualizes security data to quickly investigate the root cause of potential security issues.", ["GuardDuty", "Security Hub", "CloudTrail"]),

    ("CloudWatch", "Management", "Monitoring and observability service collecting metrics, logs, alarms and dashboards across AWS resources.", ["CloudTrail", "Auto Scaling", "EventBridge", "X-Ray", "SNS"]),
    ("CloudTrail", "Management", "Records account activity and API calls across AWS for governance, compliance and auditing.", ["CloudWatch", "Config", "GuardDuty", "S3"]),
    ("CloudFormation", "Management", "Infrastructure-as-code service that provisions and manages AWS resources via declarative templates.", ["CDK", "Service Catalog", "Systems Manager", "Control Tower"]),
    ("Config", "Management", "Continuously assesses, audits and records resource configurations and evaluates them against desired rules.", ["CloudTrail", "Security Hub", "Systems Manager", "Organizations"]),
    ("Systems Manager", "Management", "Unified interface to view operational data and automate tasks (patching, run command, parameters) across resources.", ["CloudWatch", "Secrets Manager", "Config", "EC2"]),
    ("Organizations", "Management", "Centrally govern and manage multiple AWS accounts with consolidated billing and service control policies.", ["Control Tower", "IAM Identity Center", "Config", "Resource Access Manager"]),
    ("Control Tower", "Management", "Sets up and governs a secure, multi-account AWS environment based on best-practice landing zones.", ["Organizations", "IAM Identity Center", "Config", "Service Catalog"]),
    ("Trusted Advisor", "Management", "Provides real-time best-practice recommendations across cost, performance, security, fault tolerance and limits.", ["Cost Explorer", "Compute Optimizer", "Security Hub"]),
    ("Service Catalog", "Management", "Lets organizations create and manage catalogs of approved IT services for consistent governance.", ["CloudFormation", "Control Tower", "Organizations"]),
    ("CDK", "Management", "Cloud Development Kit to define cloud infrastructure as code using familiar programming languages.", ["CloudFormation", "CodePipeline"]),
    ("OpsWorks", "Management", "Configuration management service using managed Chef and Puppet to automate server configuration.", ["EC2", "CloudFormation", "Systems Manager"]),
    ("Cost Explorer", "Management", "Visualize, understand and forecast AWS spending and usage over time.", ["Budgets", "Compute Optimizer", "Trusted Advisor"]),
    ("Budgets", "Management", "Set custom cost and usage budgets that alert when thresholds are exceeded or forecast to be.", ["Cost Explorer", "SNS", "Trusted Advisor"]),
    ("Compute Optimizer", "Management", "Recommends optimal AWS resources to reduce cost and improve performance using machine learning.", ["Cost Explorer", "Trusted Advisor", "EC2"]),
    ("Resource Access Manager", "Management", "Securely shares AWS resources such as subnets and Transit Gateways across accounts.", ["Organizations", "Transit Gateway", "VPC"]),

    ("SQS", "Integration", "Fully managed message queuing service that decouples and scales microservices and distributed systems.", ["SNS", "Lambda", "EventBridge", "Step Functions"]),
    ("SNS", "Integration", "Fully managed pub/sub messaging for application-to-application and application-to-person notifications.", ["SQS", "Lambda", "EventBridge", "SES"]),
    ("EventBridge", "Integration", "Serverless event bus that connects application data from your apps, SaaS and AWS services using rules.", ["Lambda", "SQS", "SNS", "Step Functions", "CloudWatch"]),
    ("Step Functions", "Integration", "Serverless orchestration service to coordinate distributed components into visual workflows (state machines).", ["Lambda", "SQS", "SNS", "EventBridge", "Batch"]),
    ("AppSync", "Integration", "Managed GraphQL service that connects apps to data sources with real-time and offline capabilities.", ["DynamoDB", "Lambda", "Cognito", "API Gateway"]),
    ("MQ", "Integration", "Managed message broker for Apache ActiveMQ and RabbitMQ to ease migration of existing messaging apps.", ["SQS", "SNS"]),
    ("SWF", "Integration", "Simple Workflow Service for building applications that coordinate work across distributed components.", ["Step Functions", "SQS"]),

    ("Kinesis", "Analytics", "Platform to collect, process and analyze real-time streaming data (Data Streams, Firehose, Analytics).", ["Data Firehose", "Lambda", "S3", "Redshift", "OpenSearch"]),
    ("Athena", "Analytics", "Serverless interactive query service to analyze data in S3 using standard SQL, paying per query.", ["S3", "Glue", "QuickSight", "Lake Formation"]),
    ("Glue", "Analytics", "Serverless data integration and ETL service with a central metadata catalog for preparing data for analytics.", ["S3", "Athena", "Redshift", "Lake Formation", "EMR"]),
    ("EMR", "Analytics", "Managed big data platform to run Apache Spark, Hadoop, Hive and Presto at scale.", ["S3", "Redshift", "Glue", "EC2"]),
    ("QuickSight", "Analytics", "Scalable, serverless business intelligence service for dashboards and ML-powered insights.", ["Redshift", "Athena", "S3", "RDS"]),
    ("OpenSearch", "Analytics", "Managed OpenSearch/Elasticsearch service for search, log analytics and observability use cases.", ["Kinesis", "Data Firehose", "CloudWatch", "S3"]),
    ("MSK", "Analytics", "Fully managed Apache Kafka service for building and running streaming data applications.", ["Kinesis", "Lambda", "S3"]),
    ("Lake Formation", "Analytics", "Simplifies building, securing and managing data lakes with centralized permissions over S3 data.", ["S3", "Glue", "Athena", "Redshift"]),
    ("Data Firehose", "Analytics", "Reliably loads streaming data into data lakes, warehouses and analytics services in near real time.", ["Kinesis", "S3", "Redshift", "OpenSearch"]),

    ("CodePipeline", "Developer", "Fully managed continuous delivery service that automates build, test and deploy pipelines.", ["CodeBuild", "CodeDeploy", "CodeCommit", "CloudFormation"]),
    ("CodeBuild", "Developer", "Fully managed CI service that compiles source, runs tests and produces deployable artifacts.", ["CodePipeline", "CodeCommit", "ECR"]),
    ("CodeDeploy", "Developer", "Automates application deployments to EC2, Lambda, ECS and on-premises servers.", ["CodePipeline", "EC2", "Lambda", "ECS"]),
    ("CodeCommit", "Developer", "Fully managed source control service hosting secure private Git repositories.", ["CodePipeline", "CodeBuild"]),
    ("X-Ray", "Developer", "End-to-end distributed tracing that follows a request as it travels across microservices, serverless functions, and APIs. Each request becomes a trace built from segments/subsegments and drawn as a service map that pinpoints latency bottlenecks, errors, faults, and throttles; sampling keeps overhead low, and annotations let you filter traces by business attributes. Instrument with the X-Ray SDK or OpenTelemetry (ADOT), with near-zero-config tracing for Lambda, API Gateway, ECS/EKS, and App Mesh; traces tie into CloudWatch (ServiceLens) for unified observability.", ["CloudWatch", "Lambda", "API Gateway", "App Mesh", "ECS", "EKS"]),

    ("SageMaker", "ML/AI", "Fully managed platform to build, train and deploy machine learning models at scale.", ["S3", "Bedrock", "Comprehend", "Rekognition"]),
    ("Rekognition", "ML/AI", "Adds image and video analysis—object, scene, face and text detection—to applications using deep learning.", ["S3", "SageMaker", "Comprehend"]),
    ("Comprehend", "ML/AI", "Natural language processing service that uncovers insights and relationships in text.", ["SageMaker", "Textract", "Translate"]),
    ("Textract", "ML/AI", "Automatically extracts text, handwriting and structured data from scanned documents.", ["Comprehend", "S3", "Rekognition"]),
    ("Bedrock", "ML/AI", "Fully managed service to build generative AI apps using foundation models via a single API.", ["SageMaker", "Lambda", "S3"]),
    ("Transcribe", "ML/AI", "Automatic speech recognition service that converts audio to text.", ["Comprehend", "Translate", "Polly"]),
    ("Polly", "ML/AI", "Turns text into lifelike speech using deep learning for voice-enabled applications.", ["Transcribe", "Translate"]),
    ("Translate", "ML/AI", "Neural machine translation service for fast, high-quality language translation.", ["Comprehend", "Transcribe", "Polly"]),

    ("WorkSpaces", "End-User", "Managed, secure cloud desktop (DaaS) service for provisioning Windows or Linux virtual desktops.", ["AppStream 2.0", "Directory Service" if False else "IAM Identity Center"]),
    ("AppStream 2.0", "End-User", "Fully managed application streaming service that delivers desktop apps to a browser.", ["WorkSpaces", "S3"]),
    ("SES", "Integration", "Simple Email Service for high-scale transactional, marketing and notification email sending and receiving.", ["SNS", "Lambda", "S3"]),
    ("Amplify", "Developer", "Set of tools and a hosting service to build and deploy full-stack web and mobile applications quickly.", ["Cognito", "AppSync", "API Gateway", "S3"]),
]


# --- Hand-authored descriptions recovered from the 2026-06-16 Anki backup ----
# These 27 richer descriptions were written by hand in Anki and were lost when
# the deck was re-imported on 2026-06-17 (the import matched notes by GUID and
# overwrote their fields with the plain generated text). They are kept here as
# the source of truth so they survive future rebuilds. They contain HTML (bold,
# lists, links); the Description field is emitted raw (not escaped) by both
# build_deck.py and build_deck_v2.py, so the markup renders.
RICH_DESCRIPTIONS = {
    'API Gateway': 'Fully managed service to create, publish and secure REST, HTTP and WebSocket APIs at any scale. Shock absorber for your backend systems.<br><br>AWS API Gateway is essentially a fully managed "front door" for your applications.<sup></sup> What makes it special isn\'t just that it acts as a <b>reverse proxy</b>, but rather how tightly integrated it is into the AWS ecosystem and how much operational heavy lifting it abstracts away from your backend code.<br><br>API Gateway moves routing, security, and throttling logic to the network edge so your application servers don\'t manage it.',
    'Amplify': 'Set of tools and a hosting service to build and deploy full-stack web and mobile applications quickly.<br><br><div><div>Deploy an app frontend with easy <b>Git-based workflows</b> and support for any <b>server-side web framework</b>. Zero-config Next.js and Nuxt deployments offer global availability, reliability, and lower latency from the Amazon CloudFront Global Edge Network in just a few clicks. Fully-managed CI/CD and automatic scale make pushing new features to high-traffic web applications seamless.</div></div><br>',
    'App Runner': 'Now ECS Express Mode.&nbsp; Fully managed service to build and run containerized web apps and APIs directly from source or an image.&nbsp; AWS App Runner <b>will no longer accept new customers</b> starting on April 30, 2026. Your existing App Runner services will remain operational and accessible. AWS continues to invest in security and availability, but we do not plan to introduce new features. For deploying and running containerized applications, we recommend&nbsp;<a href="https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-service-overview.html">Amazon ECS Express Mode</a>&nbsp;, a new capability in&nbsp;<a href="https://aws.amazon.com/ecs/">Amazon ECS</a>. To learn more, see our&nbsp;<a href="https://docs.aws.amazon.com/apprunner/latest/dg/apprunner-availability-change.html">migration guidance</a>.<div><div><div><div><div><div><div><div><div><div><div></div></div></div></div></div></div></div></div></div></div></div><br>',
    'AppStream 2.0': '<div><div><div><b>Amazon WorkSpaces</b> applications (formerly AppStream 2.0) offers a fully managed solution to deliver software-as-a-service (SaaS) and web-based applications and transform desktop applications into cloud-based services without code changes. It enables global scalability without infrastructure management and supports&nbsp;<a href="https://aws.amazon.com/workspaces/applications/faqs/">multi-session capabilities</a>, optimizing resource use and costs across various user types.&nbsp;</div><div>Available in preview,&nbsp;<a href="https://aws.amazon.com/blogs/aws/modernize-your-workflows-amazon-workspaces-now-gives-ai-agents-their-own-desktop-preview/">these features now extend to AI agents</a>&nbsp;with WorkSpaces applications, bridging agentic AI to the desktop applications enterprises already run, giving both people and agents secure, scalable application access from a single service.</div></div></div>',
    'AppSync': 'Managed GraphQL service that <b>connects apps</b> to <b>data sources</b> with real-time and offline capabilities.<br><br>AWS AppSync gets its name because its primary function is to <b>synchronize application data</b> seamlessly between <b>mobile/web frontends</b> and <b>backend data sources</b> (like databases or APIs) in real time, using GraphQL. [<a href="https://aws.amazon.com/blogs/mobile/appsync-custom-auth/">1</a>, <a href="https://aws.amazon.com/blogs/aws/introducing-amazon-appsync/">2</a>]<br><ul><li>Use AWS AppSync to simplify integration with AI backends like Amazon Bedrock.</li><li>Combine multiple GraphQL source APIs into a single Merged GraphQL API “super graph."</li><li>Introspect your SQL and NoSQL databases and automatically create an API layer.</li><li>Create a pub/sub solution for your real-time events</li></ul><br>',
    'Athena': 'Serverless interactive query service to analyze data in S3 using standard SQL, paying per query.<br><br><div><div><div>Amazon Athena is an interactive query service that simplifies data analysis in&nbsp;<a href="https://aws.amazon.com/s3/">Amazon S3</a>&nbsp;using standard SQL. Amazon named the service "Athena" after the Greek goddess of wisdom, strategy, and knowledge. The name was chosen because the service is designed to derive intelligence and extract valuable business insights from raw data. [<a href="https://clearscale.com/what-is-athena-an-overview-of-the-aws-query-service/">1</a>, <a href="https://www.linkedin.com/pulse/amazon-athena-what-why-how-jubin-sanghvi">2</a>, <a href="https://redskydigital.com/us/unlocking-serverless-data-querying-with-amazon-athena-in-aws/">3</a>]</div></div></div>',
    'Bedrock': '<div><div><strong>Amazon Bedrock</strong> is a fully managed cloud service that enables developers to build and scale generative artificial intelligence applications. It acts as a serverless platform that provides access to high-performing <strong>foundation models (FMs)</strong> from leading AI companies through a single, unified API. [<a href="https://aws.amazon.com/video/watch/1fec548f4d2/">1</a>, <a href="https://en.wikipedia.org/wiki/Amazon_Bedrock">2</a>, <a href="https://www.pump.co/blog/aws-bedrock/">3</a>]<br></div></div>',
    'CDK': '<b>Cloud Development Kit</b> to define cloud infrastructure as code using familiar programming languages.',
    'Cloud Map': '<div><div>AWS Cloud Map is a managed resource discovery service that acts as a dynamic phonebook for your architecture. It lets applications find microservices and resources using custom names instead of hardcoded IP addresses.</div><div><b>Core Features:</b></div><ul><li><div><b>Dynamic Registry:</b> Automatically updates resource locations as your infrastructure scales.</div></li><li><div><b>Flexible Discovery:</b> Applications locate dependencies via DNS (Amazon Route 53) or the Cloud Map API.</div></li><li><div><b>Health Checking:</b> Automatically routes traffic away from failing or unhealthy instances.</div></li></ul><div><b>Takeaway</b></div><div>It decouples services from underlying infrastructure, preventing routing failures caused by IP address churn in microservice environments.</div></div>',
    'Config': '<ul><li><font color="#232b37">Continually assess, monitor, and record resource configuration changes to simplify change management.</font></li><li><span style="color: rgb(35, 43, 55);">Audit and evaluate compliance of your resource configurations with your organization’s policies on a continual basis.</span></li><li><span style="color: rgb(35, 43, 55);">Simplify operational troubleshooting by correlating configuration changes to particular events in your account.</span></li></ul>',
    'Direct Connect': '<div><div><div><div><div><div><div><div><div><div><div><div><div><div>The AWS Direct Connect cloud service is the shortest path to your AWS resources. While in transit, your network traffic remains on the AWS global network and never touches the public internet. This reduces the chance of hitting bottlenecks or unexpected increases in latency. When creating a new connection, you can choose a hosted connection provided by an AWS Direct Connect Delivery Partner, or choose a dedicated connection from AWS—and deploy at AWS Direct Connect locations around the globe. With AWS Direct Connect SiteLink, you can send data between AWS Direct Connect locations to create private network connections between the offices and data centers in your global network.</div></div></div></div></div></div></div></div></div></div></div></div></div></div><div><div><div><div><div><div><div><div><div><div><div><div></div></div></div></div></div></div></div></div></div></div></div></div><br>',
    'EFS': 'AWS EFS stands for <strong>Elastic File System</strong>.&nbsp; Fully managed elastic NFS file system that can be mounted by many EC2 instances concurrently across AZs.',
    'Fargate': '<div><div>AWS Fargate is a serverless compute engine for containers that integrates natively with Amazon ECS and EKS, eliminating the need to manage underlying servers.</div><div><b>Core Features:</b></div><ul><li><div><b>Serverless Abstraction:</b> Removes the operational overhead of provisioning, patching, and scaling cluster infrastructure.</div></li><li><div><b>Precise Billing:</b> You specify and pay only for the exact vCPU and memory resources your containers consume per second.</div></li><li><div><b>Isolated Security:</b> Each task runs in its own dedicated, isolated compute environment for strong workload boundaries.</div></li></ul><div><b>Takeaway</b></div><div>Fargate shifts your focus entirely from managing infrastructure to deploying applications, streamlining orchestration and automated scaling for containerized microservices.</div></div>',
    'Glue': 'Serverless data integration and ETL service with a central metadata catalog for preparing data for analytics.<br><br><div><div><div>AWS Glue is a fully managed, serverless extract, transform, and load (ETL) service.<sup></sup> At its core, it removes the heavy lifting of provisioning, configuring, and scaling the underlying compute infrastructure (like transient EMR clusters) required to execute massive data integration and transformation jobs.<sup></sup><br></div></div></div>',
    'MSK': 'AWS MSK stands for <strong>Amazon Managed Streaming for Apache Kafka</strong>.&nbsp; Fully managed Apache Kafka service for building and running streaming data applications.&nbsp; Named "Kafka" because it writes, like the writer.<br><br>Apache Kafka is an open-source, distributed event streaming platform used to collect, store, process, and route high-volume streaming data in real-time. It acts as a highly scalable message broker, allowing various applications and services to publish (write) and subscribe to (read) streams of events without depending on each other directly. [<a href="https://kafka.apache.org/">1</a>, <a href="https://www.confluent.io/what-is-apache-kafka/">2</a>, <a href="https://www.ibm.com/think/topics/apache-kafka">3</a>, <a href="https://kafka.apache.org/intro/">4</a>, <a href="https://cloud.google.com/learn/what-is-apache-kafka">5</a>]',
    'Neptune': '<div><div><div><div><div><div>Neptune instantly scales <b>graph workloads</b>, removing the need to manage capacity. By modeling data as a graph, Neptune captures context that improves accuracy and explainability of generative AI applications. To make AI application development easier, <b>Neptune offers fully managed GraphRAG</b> with Amazon Bedrock Knowledge Bases, and integrations with <b>Strands AI Agents SDK</b> and popular agentic memory tools. It also easily analyzes tens of billions of relationships across structured and unstructured data within seconds delivering strategic insights. Neptune is the only database that gives you the power of connected data with the enterprise capabilities and value of AWS.</div></div></div></div></div></div><div><div><div><div><div><div><div><div><div><span style="background-color: rgba(0, 0, 0, 0); color: rgb(22, 29, 38) !important;"></span></div></div></div></div></div></div></div></div></div><br>',
    'OpenSearch': 'Like Splunk, Managed OpenSearch/Elasticsearch service for search, <b>log analytics</b> and <b>observability</b> use cases.',
    'QLDB': 'Quantum Ledger Database. Fully managed <b>ledger database</b> providing a transparent, immutable, cryptographically verifiable transaction log.&nbsp; QLDB sends <b>service events</b> directly to EventBridge, as well as via AWS CloudTrail.<br><br><strong>Quantization (Q):</strong> Refers to tracking and capturing the absolute minimum, indivisible unit of data change ("quantum") in an application.<br><strong>Ledger (L):</strong> Represents its core function: maintaining an authoritative, chronological log of all transactions and data alterations.',
    'SQS': 'Fully managed message queuing service that decouples and scales microservices and distributed systems.<br><br>AWS SQS (Simple Queue Service) is primarily used to <strong>decouple</strong> and scale different parts of a software application. Instead of services talking to each other directly and forcing one to wait for the other, they send messages to a queue, ensuring seamless background processing and preventing system crashes during traffic spikes. [<a href="https://aws.amazon.com/sqs/">1</a>, <a href="https://www.dash0.com/knowledge/aws-sqs">2</a>]',
    'SWF': 'Simple Workflow Service ( Step Functions newer ) is highly programmable for building applications that coordinate work across <b>distributed components</b>.<br><br><div>Amazon Simple Workflow Service (Amazon SWF) helps developers build, run, and scale <b>background jobs</b> that have <b>parallel</b> or <b>sequential </b>steps. You can think of Amazon SWF as a fully-managed <b>state tracker</b> and <b>task coordinator</b> in&nbsp;<a href="https://aws.amazon.com/what-is-cloud-computing/">the Cloud</a>.</div><br>',
    'Shield': '<div>AWS Shield protects networks and applications by identifying network security configuration issues and defending applications against active web exploitation and distributed denial of service (DDoS) events.&nbsp;AWS Shield does this by offering two key capabilities:&nbsp;</div><div><br></div><div><div><span style="background-color: rgba(0, 0, 0, 0); color: rgb(35, 43, 55);"><div><b>AWS Shield network security director (in preview)</b>&nbsp;performs an analysis of your resources to help you visualize your network topology, identify configuration issues, and receive actionable remediation recommendations.</div><div><br></div><div><b>AWS Shield Advanced</b>&nbsp;offers managed DDoS protection for continuous automatic mitigation of sophisticated DDoS events to minimize application downtime and latency. You can customize your DDoS protection strategy using application-specific security controls and expert guidance from the Shield Response Team during active DDoS incidents.&nbsp;</div></span></div><div><h3></h3><span style="background-color: rgba(0, 0, 0, 0); color: rgb(35, 43, 55);"></span></div><br></div>',
    'Step Functions': '<div><div><span style="background-color: rgba(0, 0, 0, 0); color: rgb(35, 43, 55);">Transform complex business logic into clear visual workflows through a drag-and- drop interface, enabling faster development and easier troubleshooting.&nbsp;</span></div><div><br></div><div>Step Functions is the <b>modern</b>, <b>serverless</b>, and <b>visual default</b> for AWS-native workflows. SWF is an older, highly programmable service primarily used for specialized workloads that require custom decider code or intricate, state-heavy human-in-the-loop&nbsp;<br></div></div><div><span style="background-color: rgba(0, 0, 0, 0); color: rgb(35, 43, 55);"><br></span></div><div><span style="color: rgb(51, 51, 51);"><span style="background-color: rgba(0, 0, 0, 0); color: rgb(22, 29, 38);">Orchestrate (&nbsp;</span></span><span style="background-color: rgba(0, 0, 0, 0); color: rgb(22, 29, 38);">Large-scale parallel workloads, microservices, automate sec &amp; IT functions, agentic workflows )</span></div>',
    'Storage Gateway': '<div>AWS Storage Gateway is a hybrid cloud storage service that enables your on-premises applications to seamlessly use AWS cloud storage. It bridges the gap between local infrastructure and the AWS storage ecosystem (Amazon S3, Amazon S3 Glacier, Amazon EBS, and Amazon FSx) by providing low-latency local access via standard storage protocols.</div><div><br></div><div>It is deployed as a virtual machine (VMware ESXi, Microsoft Hyper-V, Linux KVM) or a physical hardware appliance directly within your local data center.</div><h2></h2>',
    'Transcribe': 'Automatic <b>speech recognition</b> service that converts audio to text.',
    'Transit Gateway': 'Central hub that <b>connects VPCs</b> and <b>on-premises networks</b> through a single gateway, simplifying routing.<br><br><div><div><div>AWS Transit Gateway helps you design and implement networks at scale by acting as a <b>cloud router</b>. As your network grows, the complexity of managing incremental connections can slow you down. AWS Transit Gateway connects VPCs and on-premises networks through a central hub.</div></div></div><br>',
    'VPC': '<b>Logically isolated virtual network</b> where you launch AWS resources with full control over IP, subnets and routing.',
    'WAF': 'Web Application Firewall that protects apps from common exploits with customizable rules.<br><br>WAF is an app-layer rule, AWS Shield is a DDoS protector ( L3/4), Network Firewall is for the VPC network.',
    'DMS': 'Database <b>Migration</b> Service moves databases and analytics workloads to AWS while the source stays live, keeping downtime to minutes. It runs on a managed replication instance that reads from the source, applies any needed transformation, and writes to the target; with change data capture (CDC) it continuously replicates ongoing changes so source and target stay in sync until you cut over. It handles homogeneous moves (e.g., Oracle→Oracle) and heterogeneous ones (e.g., Oracle→Aurora PostgreSQL) — for heterogeneous, the companion Schema Conversion Tool (SCT) converts schemas and code first. Sources/targets include on-prem and cloud relational engines, plus targets like S3, Redshift, DynamoDB, and Kinesis. Use it to migrate to AWS, replicate across regions/accounts, or feed a data lake — not for ongoing application queries.',
    'Detective': '<div><div>Amazon Detective automatically collects log data from your AWS resources and uses machine learning (ML), statistical analysis, and graph theory to build a dataset that you can use to conduct more efficient security investigations.</div></div>',
    'Inspector': '<div><div><div>Amazon Inspector automatically discovers workloads, such as Amazon Elastic Compute Cloud (Amazon EC2) instances, container images, and AWS Lambda functions, as well as code repositories, and <b>scans them for software vulnerabilities and unintended network exposure.</b></div></div></div><br>',
    'Keyspaces': "Serverless, fully managed wide-column NoSQL database compatible with <b>Apache Cassandra</b>. You use the same CQL (Cassandra Query Language), drivers, and tools you'd use with Cassandra, but AWS runs it for you — no clusters, nodes, or patching to manage, and it scales tables up and down automatically with pay-per-request or provisioned capacity. <b>Data is replicated across 3 Availability Zones for durability</b>, with single-digit-millisecond performance at scale. Its 'wide-column' model stores rows whose columns can vary, partitioned by a key — ideal for high-volume, write-heavy workloads like time-series, IoT device data, and user activity feeds. Pick it to migrate or build Cassandra workloads without operating the cluster.",
    'Resource Access Manager': '<div>AWS Resource Access Manager (RAM) is a service that allows you to <b>share specific AWS resources across multiple AWS accounts</b>, within your AWS Organization, or with individual AWS accounts.<sup></sup> </div><div>It is designed to solve the problem of managing resources in multi-account environments where you would otherwise have to manually replicate the same resources (like VPC subnets or license configurations) in every account, which creates operational overhead and consistency challenges.<sup></sup></div>',
}

# Apply the recovered descriptions over the plain fallbacks defined above.
_unknown = set(RICH_DESCRIPTIONS) - {n for n, *_ in SERVICES}
if _unknown:
    raise SystemExit(f"RICH_DESCRIPTIONS names not in SERVICES: {sorted(_unknown)}")
SERVICES = [
    (name, cat, RICH_DESCRIPTIONS.get(name, desc), assoc)
    for name, cat, desc, assoc in SERVICES
]


def assoc_html(names):
    parts = []
    for n in names:
        url = URL.get(n)
        if url:
            parts.append(f'<a href="{html.escape(url)}">{html.escape(n)}</a>')
        else:
            parts.append(html.escape(n))
    return ", ".join(parts)


model = genanki.Model(
    1607392319,
    "AWS Service Card",
    fields=[
        {"name": "Service"},
        {"name": "Category"},
        {"name": "Description"},
        {"name": "Associated"},
        {"name": "ServiceLink"},
    ],
    templates=[{
        "name": "Card 1",
        "qfmt": '<div class="svc"><a href="{{ServiceLink}}">{{Service}} <span class="ext">&#8599;</span></a></div><div class="cat">{{Category}}</div>',
        "afmt": '''{{FrontSide}}<hr id="answer">
<div class="desc">{{Description}}</div>
<div class="assoc-label">Often associated with:</div>
<div class="assoc">{{Associated}}</div>''',
    }],
    css='''.card { font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 18px; text-align: center; color: #232f3e; background: #fff; padding: 16px; }
.svc { font-size: 28px; font-weight: 700; }
.svc a { color: #ec7211; text-decoration: none; }
.svc a:hover { text-decoration: underline; }
.svc .ext { font-size: 16px; vertical-align: 1px; }
.cat { font-size: 13px; letter-spacing: 1px; text-transform: uppercase; color: #687078; margin-top: 4px; }
.desc { font-size: 17px; line-height: 1.5; margin: 12px auto; max-width: 540px; text-align: left; }
.assoc-label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #687078; margin-top: 14px; }
.assoc { font-size: 16px; line-height: 1.7; margin-top: 4px; }
.assoc a { color: #0073bb; text-decoration: none; }
.assoc a:hover { text-decoration: underline; }
hr#answer { border: none; border-top: 1px solid #d5dbdb; margin: 14px 0; }''',
)

if __name__ == "__main__":
    deck = genanki.Deck(2059400110, "AWS Solutions Architect — Services")

    missing_url = [name for name, *_ in SERVICES if name not in URL]
    if missing_url:
        raise SystemExit(f"Missing homepage URL for: {missing_url}")

    for name, cat, desc, assoc in SERVICES:
        note = genanki.Note(
            model=model,
            fields=[name, cat, desc, assoc_html(assoc), URL[name]],
        )
        deck.add_note(note)

    # Note: build_deck_v2.py is the canonical builder. Running this module
    # directly rebuilds the legacy v1 (links-only) deck as a separate file
    # so it won't clobber the shipped AWS_Services.apkg.
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "AWS_Services_v1.apkg")
    genanki.Package(deck).write_to_file(out)
    print(f"Wrote {len(SERVICES)} cards to {os.path.normpath(out)}")
