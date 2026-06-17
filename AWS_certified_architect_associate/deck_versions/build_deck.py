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
    ("X-Ray", "Developer", "Distributed tracing service that helps analyze and debug production and distributed applications.", ["CloudWatch", "Lambda", "API Gateway", "App Mesh"]),

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
