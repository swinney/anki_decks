# Best-practices page per service: name -> AWS best-practices URL.
#
# Each URL was researched and verified to resolve (HTTP 200) to a genuine AWS
# best-practices resource. Where a service has a dedicated "Best practices for
# <service>" page it is used; otherwise the most authoritative AWS best-practices
# resource for that service (security best practices, a Well-Architected/
# prescriptive-guidance page, or an AWS best-practices whitepaper).
#
# Three services have no best-practices page (QLDB and OpsWorks are end-of-life
# with docs removed; Cloud Map has none), so they point to WELL_ARCHITECTED.

WELL_ARCHITECTED = (
    "https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html"
)

BEST_PRACTICES = {
    # Compute
    "EC2": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-best-practices.html",
    "Lambda": "https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html",
    "ECS": "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-best-practices.html",
    "EKS": "https://docs.aws.amazon.com/eks/latest/best-practices/introduction.html",
    "Fargate": "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/security-fargate.html",
    "Elastic Beanstalk": "https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/security-best-practices.html",
    "Lightsail": "https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-bucket-security-best-practices.html",
    "Batch": "https://docs.aws.amazon.com/batch/latest/userguide/best-practices.html",
    "Auto Scaling": "https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/amazon-ec2-with-auto-scaling-bp7.html",
    "Outposts": "https://docs.aws.amazon.com/whitepapers/latest/aws-outposts-high-availability-design/aws-outposts-high-availability-design.html",
    "App Runner": "https://docs.aws.amazon.com/apprunner/latest/dg/security-best-practices.html",
    "ECR": "https://docs.aws.amazon.com/config/latest/developerguide/security-best-practices-for-ECR.html",
    # Storage
    "S3": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html",
    "S3 Glacier": "https://docs.aws.amazon.com/amazonglacier/latest/dev/security.html",
    "EBS": "https://docs.aws.amazon.com/ebs/latest/userguide/ebs-performance.html",
    "EFS": "https://docs.aws.amazon.com/efs/latest/ug/performance.html",
    "FSx": "https://docs.aws.amazon.com/fsx/latest/WindowsGuide/windows-best-practices.html",
    "Storage Gateway": "https://docs.aws.amazon.com/storagegateway/latest/tgw/best-practices.html",
    "AWS Backup": "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-best-practices/welcome.html",
    "Snowball": "https://docs.aws.amazon.com/snowball/latest/developer-guide/BestPractices.html",
    "DataSync": "https://aws.amazon.com/blogs/storage/best-practices-for-setting-up-your-aws-datasync-agent/",
    # Database
    "RDS": "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html",
    "Aurora": "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_BestPractices.Security.html",
    "DynamoDB": "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html",
    "ElastiCache": "https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/BestPractices.html",
    "Redshift": "https://docs.aws.amazon.com/redshift/latest/dg/best-practices.html",
    "Neptune": "https://docs.aws.amazon.com/neptune/latest/userguide/best-practices.html",
    "DocumentDB": "https://docs.aws.amazon.com/documentdb/latest/devguide/best_practices.html",
    "Keyspaces": "https://docs.aws.amazon.com/keyspaces/latest/devguide/best-practices.html",
    "Timestream": "https://docs.aws.amazon.com/timestream/latest/developerguide/best-practices.html",
    "QLDB": WELL_ARCHITECTED,  # service end-of-life; docs removed
    "DMS": "https://docs.aws.amazon.com/dms/latest/userguide/CHAP_BestPractices.html",
    "MemoryDB": "https://docs.aws.amazon.com/memorydb/latest/devguide/bestpractices.html",
    # Networking
    "VPC": "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html",
    "Route 53": "https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/best-practices.html",
    "CloudFront": "https://docs.aws.amazon.com/config/latest/developerguide/security-best-practices-for-CloudFront.html",
    "ELB": "https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/elastic-load-balancing-bp6.html",
    "API Gateway": "https://docs.aws.amazon.com/apigateway/latest/developerguide/security-best-practices.html",
    "Direct Connect": "https://docs.aws.amazon.com/directconnect/latest/UserGuide/disaster-recovery-resiliency.html",
    "Transit Gateway": "https://docs.aws.amazon.com/vpc/latest/tgw/tgw-best-design-practices.html",
    "Global Accelerator": "https://docs.aws.amazon.com/global-accelerator/latest/dg/best-practices-aga.html",
    "PrivateLink": "https://docs.aws.amazon.com/whitepapers/latest/aws-privatelink/aws-privatelink.html",
    "VPN": "https://docs.aws.amazon.com/vpn/latest/s2svpn/cgw-best-practice.html",
    "App Mesh": "https://docs.aws.amazon.com/app-mesh/latest/userguide/best-practices.html",
    "Cloud Map": WELL_ARCHITECTED,  # no best-practices page exists
    # Security
    "IAM": "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html",
    "IAM Identity Center": "https://docs.aws.amazon.com/singlesignon/latest/userguide/security.html",
    "Cognito": "https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-security-best-practices.html",
    "KMS": "https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-kms-best-practices/introduction.html",
    "CloudHSM": "https://docs.aws.amazon.com/cloudhsm/latest/userguide/best-practices.html",
    "Secrets Manager": "https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html",
    "WAF": "https://docs.aws.amazon.com/waf/latest/developerguide/waf-managed-protections-best-practices.html",
    "Shield": "https://docs.aws.amazon.com/waf/latest/developerguide/ddos-resiliency.html",
    "GuardDuty": "https://docs.aws.amazon.com/guardduty/latest/ug/security.html",
    "Inspector": "https://docs.aws.amazon.com/inspector/latest/user/security.html",
    "Macie": "https://docs.aws.amazon.com/macie/latest/user/security.html",
    "Security Hub": "https://docs.aws.amazon.com/securityhub/latest/userguide/fsbp-standard.html",
    "ACM": "https://docs.aws.amazon.com/acm/latest/userguide/acm-bestpractices.html",
    "Firewall Manager": "https://docs.aws.amazon.com/waf/latest/developerguide/fms-security.html",
    "Network Firewall": "https://docs.aws.amazon.com/network-firewall/latest/developerguide/compliance.html",
    "Detective": "https://docs.aws.amazon.com/detective/latest/userguide/security-best-practices.html",
    # Developer
    "CodePipeline": "https://docs.aws.amazon.com/codepipeline/latest/userguide/security-best-practices.html",
    "CodeBuild": "https://docs.aws.amazon.com/codebuild/latest/userguide/security.html",
    "CodeDeploy": "https://docs.aws.amazon.com/codedeploy/latest/userguide/security.html",
    "CodeCommit": "https://docs.aws.amazon.com/codecommit/latest/userguide/security.html",
    "X-Ray": "https://docs.aws.amazon.com/xray/latest/devguide/security.html",
    "Amplify": "https://docs.aws.amazon.com/amplify/latest/userguide/security-best-practices.html",
    # Management
    "CloudWatch": "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/security.html",
    "CloudTrail": "https://docs.aws.amazon.com/awscloudtrail/latest/userguide/best-practices-security.html",
    "CloudFormation": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html",
    "Config": "https://docs.aws.amazon.com/config/latest/developerguide/security-best-practices.html",
    "Systems Manager": "https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-best-practices.html",
    "Organizations": "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices.html",
    "Control Tower": "https://docs.aws.amazon.com/controltower/latest/userguide/best-practices.html",
    "Trusted Advisor": "https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-12.html",
    "Service Catalog": "https://docs.aws.amazon.com/servicecatalog/latest/adminguide/security-best-practices.html",
    "CDK": "https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html",
    "OpsWorks": WELL_ARCHITECTED,  # service end-of-life; docs removed
    "Cost Explorer": "https://docs.aws.amazon.com/cost-management/latest/userguide/ce-api-best-practices.html",
    "Budgets": "https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-best-practices.html",
    "Compute Optimizer": "https://docs.aws.amazon.com/compute-optimizer/latest/ug/security.html",
    "Resource Access Manager": "https://docs.aws.amazon.com/ram/latest/userguide/security.html",
    # Integration
    "SQS": "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-best-practices.html",
    "SNS": "https://docs.aws.amazon.com/sns/latest/dg/sns-security-best-practices.html",
    "EventBridge": "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-best-practices.html",
    "Step Functions": "https://docs.aws.amazon.com/step-functions/latest/dg/sfn-best-practices.html",
    "AppSync": "https://docs.aws.amazon.com/appsync/latest/devguide/best-practices.html",
    "MQ": "https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/amazon-mq-best-practices.html",
    "SWF": "https://docs.aws.amazon.com/amazonswf/latest/developerguide/cw-metrics.html",
    "SES": "https://docs.aws.amazon.com/ses/latest/dg/best-practices.html",
    # Analytics
    "Kinesis": "https://docs.aws.amazon.com/streams/latest/dev/security-best-practices.html",
    "Athena": "https://docs.aws.amazon.com/athena/latest/ug/performance-tuning.html",
    "Glue": "https://docs.aws.amazon.com/glue/latest/dg/best-practice-catalog.html",
    "EMR": "https://docs.aws.amazon.com/prescriptive-guidance/latest/amazon-emr-hardware/best-practices.html",
    "QuickSight": "https://docs.aws.amazon.com/quicksight/latest/user/best-practices-security.html",
    "OpenSearch": "https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp.html",
    "MSK": "https://docs.aws.amazon.com/msk/latest/developerguide/bestpractices-intro.html",
    "Lake Formation": "https://docs.aws.amazon.com/lake-formation/latest/dg/lf-limitations.html",
    "Data Firehose": "https://docs.aws.amazon.com/firehose/latest/dev/security-best-practices.html",
    # ML/AI
    "SageMaker": "https://docs.aws.amazon.com/sagemaker/latest/dg/best-practice-endpoint-security.html",
    "Rekognition": "https://docs.aws.amazon.com/rekognition/latest/dg/best-practices.html",
    "Comprehend": "https://docs.aws.amazon.com/comprehend/latest/dg/idp-images-bp.html",
    "Textract": "https://docs.aws.amazon.com/textract/latest/dg/textract-best-practices.html",
    "Bedrock": "https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html",
    "Transcribe": "https://docs.aws.amazon.com/transcribe/latest/dg/security-best-practices.html",
    "Polly": "https://docs.aws.amazon.com/polly/latest/dg/security-best-practices.html",
    "Translate": "https://docs.aws.amazon.com/translate/latest/dg/ct-best-practices.html",
    # End-User Computing
    "WorkSpaces": "https://docs.aws.amazon.com/whitepapers/latest/best-practices-deploying-amazon-workspaces/best-practices-deploying-amazon-workspaces.html",
    "AppStream 2.0": "https://docs.aws.amazon.com/whitepapers/latest/best-practices-for-deploying-amazon-appstream-2/best-practices-for-deploying-amazon-appstream-2.html",
}
