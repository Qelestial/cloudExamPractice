# aws_ccp_quiz.py
import streamlit as st
import random
from dataclasses import dataclass
from typing import List, Set, Dict, Optional

# -----------------------------
# Config & helpers
# -----------------------------
st.set_page_config(page_title="CCP (CLF-C02) 150-Question Practice", layout="centered")

# Visual tweaks and simple theming
PRIMARY = "#FF9900"  # AWS orange
ACCENT = "#232F3E"    # AWS console dark

def inject_css():
    st.markdown(
        f"""
        <style>
        .stApp .block-container {{
            max-width: 900px;
        }}
        /* Buttons */
        .stButton>button {{
            border-radius: 8px;
            border: 1px solid {PRIMARY}33;
            background: linear-gradient(180deg, {PRIMARY} 0%, #e68500 100%);
            color: white;
            font-weight: 600;
            box-shadow: 0 1px 2px rgb(0 0 0 / 8%);
        }}
        .stButton>button:disabled {{
            background: #c9c9c9 !important;
            color: #6b6b6b !important;
            border-color: #c9c9c9 !important;
        }}
        /* Radio and checkbox options */
        div.stRadio > label, div.stCheckbox > label {{
            font-size: 1.05rem;
        }}
        /* Question prompt card */
        .prompt-card {{
            padding: 12px 16px;
            background: #ffffff;
            border: 1px solid #eceff1;
            border-radius: 10px;
            box-shadow: 0 1px 2px rgb(0 0 0 / 6%);
            margin-bottom: 10px;
        }}
        /* Domain pill */
        .pill {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            background: {ACCENT};
            color: #fff;
            font-size: 0.85rem;
            margin-bottom: 6px;
        }}
        /* Answer breakdown list */
        .answer-breakdown li {{
            margin-bottom: 4px;
        }}
        /* Answer row highlight */
        .answer-row {{
            background: #e8f5e9;
            border-left: 4px solid #2e7d32;
            padding: 8px 12px;
            border-radius: 6px;
            margin: 8px 0 6px 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

DOMAINS = {
    "Cloud Concepts": 0.24,
    "Security & Compliance": 0.30,
    "Cloud Tech & Services": 0.34,
    "Billing, Pricing & Support": 0.12,
}

TOTAL_QUESTIONS = 150  # as requested

def raw_to_scaled(raw: int, total: int) -> int:
    """Linear approximation of AWS scaled scoring (100–1000)."""
    pct = raw / total if total else 0
    return int(round(100 + 900 * pct))

@dataclass
class Question:
    id: int
    domain: str
    prompt: str
    options: List[str]
    correct: Set[int]     # indices of correct options (0-based)
    explanation: str
    multi: bool           # True => multiple-response; False => multiple-choice
    # Optional per-option explanations aligned with options
    option_explanations: Optional[List[str]] = None

# -----------------------------
# Option descriptions (for per-option rationales)
# -----------------------------
OPTION_DESC: Dict[str, str] = {
    # Cloud Concepts & Infra
    "Global reach": "Serve users worldwide via regions/edge locations to reduce latency.",
    "Global replication": "Replicate/caches content globally to lower latency; not pricing-related.",
    "Pay-as-you-go": "Replace CapEx with variable OpEx; pay only for what you use.",
    "Agility": "Rapid experimentation and faster time-to-market via managed services and automation.",
    "Elasticity": "Automatically add/remove capacity to match demand.",
    "Fault tolerance": "Continue operating despite component failures.",
    "Global footprint": "AWS presence in multiple regions/AZs worldwide.",
    "Edge networking": "Use edge locations (e.g., CloudFront) to cache near users and reduce latency.",
    "Shared responsibility": "Security model split between AWS (of the cloud) and customer (in the cloud).",
    "Managed services": "AWS operates underlying infrastructure so you focus on your application.",
    "Availability Zone": "One or more discrete data centers within an AWS Region.",
    "Region": "Geographic area containing multiple Availability Zones.",
    "Edge location": "Global edge sites used by CloudFront and other edge services.",
    "Local Zone": "Extend AWS compute/storage to metro areas closer to end users for low latency.",
    "Wavelength Zone": "AWS infrastructure at the 5G edge inside telecom networks.",
    "High availability": "Design for resilience and minimal downtime across failures.",
    "Manual procurement": "Traditional slow hardware/software procurement processes.",
    "Long hardware lead time": "Delays from ordering and receiving hardware on-premises.",
    "Vendor lock-in": "Being tied to a single vendor/platform with switching costs.",
    "Manual scaling": "Manually adding/removing capacity instead of automatic scaling.",
    "Data rack": "Not an AWS global infrastructure term; distractor.",

    # Security & Compliance
    "Security group": "Stateful virtual firewall at the ENI/instance level.",
    "NACL": "Stateless network ACL at the subnet boundary.",
    "Network ACL": "Stateless network ACL at the subnet boundary.",
    "IAM policy": "JSON policy document that defines permissions for identities/resources.",
    "WAF rule": "Filter web requests at Layer 7 for common exploits (OWASP).",
    "AWS CloudTrail": "Records AWS account API activity and events.",
    "Amazon CloudWatch": "Metrics, logs, dashboards, and alarms for monitoring.",
    "AWS Config": "Records/assesses resource configurations and drifts over time.",
    "Amazon GuardDuty": "Intelligent threat detection using logs and network findings.",
    "AWS Shield Advanced": "Managed DDoS protection with additional features (cost protection, support).",
    "Amazon CloudWatch Alarms": "Threshold-based notifications/actions on metrics.",
    "AWS KMS": "Managed service for creating and controlling encryption keys.",
    "Customer": "Responsibilities in the cloud (e.g., data, apps, guest OS).",
    "AWS": "Responsibilities of the cloud (e.g., hardware, regions, hypervisor).",
    "Both share": "Some controls are shared depending on the service and configuration.",
    "No one": "Not applicable in shared responsibility (used as distractor).",
    "IAM user with long-lived keys": "Static credentials; avoid embedding in code.",
    "IAM role": "Use STS to obtain temporary credentials securely.",
    "Root user": "Do not use routinely; reserve for account setup and rare tasks.",
    "Group": "Collections of users for attaching policies; not a credential source.",
    "VPC endpoint policy": "Policy to control access via interface/gateway endpoints.",
    "Route table": "Determines where traffic is directed within a VPC.",
    "AWS Artifact": "On-demand access to AWS compliance reports and agreements.",
    "AWS Organizations": "Multi-account governance and consolidated billing.",
    "AWS Secrets Manager": "Securely store and rotate secrets; not for compliance reports.",
    "AWS License Manager": "Manage and track software licenses on AWS.",

    # Technology & Services
    "Amazon EC2": "Virtual servers with full OS/network control.",
    "AWS Lambda": "Serverless functions that run code in response to events.",
    "Amazon ECS on EC2": "Container orchestration using EC2 instances as capacity.",
    "Amazon Lightsail": "Simple VPS for small apps with bundled resources.",
    "AWS Fargate": "Serverless compute for containers (no server management).",
    "Amazon EKS": "Managed Kubernetes control plane and integrations.",
    "Amazon EMR": "Managed big data frameworks (Hadoop/Spark/HBase).",
    "AWS Batch": "Batch job scheduling/execution across compute resources.",
    "AWS Glue": "Serverless data integration (ETL) service.",
    "Amazon MQ": "Managed Apache ActiveMQ/RabbitMQ message broker.",
    "Amazon S3": "Object storage with high durability and virtually unlimited scale.",
    "Amazon EBS": "Block storage for EC2 instances.",
    "Amazon EFS": "Elastic file system for Linux workloads.",
    "AWS Storage Gateway": "Hybrid storage integration between on-premises and AWS.",
    "Amazon RDS": "Managed relational databases (MySQL, Postgres, etc.).",
    "Amazon DynamoDB": "Serverless NoSQL key-value/document DB with single-digit ms latency.",
    "Amazon Redshift": "Fully managed data warehouse for analytics at scale.",
    "Amazon OpenSearch Service": "Search and analytics engine (OpenSearch/Elasticsearch-compatible).",
    "S3 Standard-IA": "Lower-cost storage for infrequent access; milliseconds retrieval across multiple AZs.",
    "S3 One Zone-IA": "Lower-cost IA in a single AZ; data lost if AZ fails.",
    "S3 Glacier Flexible Retrieval": "Archive with minutes to hours retrieval; lower cost than Standard.",
    "S3 Glacier Deep Archive": "Lowest-cost archive with hours retrieval time.",
    "S3 Standard": "General purpose storage with low latency, high throughput.",
    "S3 Glacier Instant Retrieval": "Archive class with milliseconds retrieval for rare access objects.",
    "S3 Intelligent-Tiering": "Auto-tiering to optimize cost for unknown/variable access patterns.",
    "Amazon SNS": "Pub/sub notifications with fan-out to subscribers.",
    "Amazon SQS": "Fully managed message queues to decouple components.",
    "Amazon EventBridge": "Event bus for routing events between AWS and SaaS/apps.",
    "AWS Step Functions": "Serverless workflow orchestration/state machines.",
    "VPC peering": "Network connectivity between two VPCs (same/different accounts/regions).",
    "AWS Direct Connect": "Dedicated network link from on-premises to AWS.",
    "VPC endpoints": "Private connectivity to supported AWS services within your VPC.",
    "NAT Gateway": "Allow private instances to access the internet for outbound traffic.",
    "AWS Audit Manager": "Continuously collect evidence for audits and frameworks.",

    # Billing, Pricing & Support
    "AWS TCO Calculator": "Compare on-premises vs AWS total cost of ownership (pre-migration).",
    "AWS Pricing Calculator": "Estimate AWS costs before deploying resources.",
    "AWS Cost Explorer": "Visualize and analyze historical and forecasted spend.",
    "AWS Budgets": "Set cost/usage thresholds and receive alerts.",
    "Savings Plans": "Commit to consistent usage for discounted compute rates.",
    "Spot Instances": "Use spare EC2 capacity at deep discounts with interruption risk.",
    "On-Demand": "Pay for compute with no commitment; flexible and predictable.",
    "On-Demand Instances": "Pay for compute with no commitment; flexible and predictable.",
    "Dedicated Hosts": "Physical servers dedicated to you; licensing/affinity use cases.",
    "AWS Control Tower": "Set up and govern a secure, multi-account AWS environment.",
    "AWS Billing Conductor": "Customize and share internal pricing/rates across accounts.",
    "Developer": "Business-hours support; general guidance; limited TA checks.",
    "Business": "24x7 support, production guidance, full Trusted Advisor checks.",
    "Enterprise On-Ramp": "For critical workloads; pooled TAM-like engagement; faster response.",
    "Enterprise": "Mission-critical; designated TAM; fastest response and concierge service.",
    "AWS Trusted Advisor": "Best-practice checks: cost, performance, security, fault tolerance, quotas.",
    "AWS Inspector": "Automated security assessment for EC2/ECR/Lambda (vulnerabilities).",
    "AWS Compute Optimizer": "Recommend right-sizing and instance family choices to optimize cost/perf.",
    "AWS Systems Manager": "Operate and manage your AWS resources at scale.",

    # Misc/common distractors added during normalization
    "Not applicable": "Distractor option (not applicable).",
    "All of the above": "Distractor; avoid unless clearly specified.",
    "None of the above": "Distractor; avoid unless clearly specified.",
    "Use a third-party tool": "Generic distractor; AWS-native options typically preferred.",
    "Refactor the app": "Generic distractor; not specific to the question.",
}

def describe_option(label: str) -> str:
    return OPTION_DESC.get(label, "")

# -----------------------------
# Question factories (templates)
# -----------------------------
def make_mcq(idc, domain, prompt, options, correct_idx, explanation, option_explanations: Optional[List[str]] = None):
    return Question(
        id=idc, domain=domain, prompt=prompt, options=options,
        correct={correct_idx}, explanation=explanation, multi=False,
        option_explanations=option_explanations
    )

def make_mrq(idc, domain, prompt, options, correct_indices, explanation, option_explanations: Optional[List[str]] = None):
    return Question(
        id=idc, domain=domain, prompt=prompt, options=options,
        correct=set(correct_indices), explanation=explanation, multi=True,
        option_explanations=option_explanations
    )

def cc_concepts_templates(start_id: int, need: int, rng: random.Random) -> List[Question]:
    """Cloud Concepts question generator."""
    q: List[Question] = []
    idc = start_id

    # A small static bank
    q.append(make_mcq(
        idc, "Cloud Concepts",
        "Which AWS pricing advantage directly replaces high up-front capital expense with variable expense?",
        ["Global reach", "Pay-as-you-go", "Shared responsibility", "Managed services"],
        1,
        "Pay-as-you-go converts CapEx to OpEx—core to cloud economics."
    )); idc += 1

    q.append(make_mcq(
        idc, "Cloud Concepts",
        "Which AWS concept describes automatically acquiring or releasing resources to match demand?",
        ["Fault tolerance", "Elasticity", "Global footprint", "Agility"],
        1,
        "Elasticity means scaling capacity up/down automatically to meet demand."
    )); idc += 1

    q.append(make_mrq(
        idc, "Cloud Concepts",
        "Select TWO pillars of the AWS Well-Architected Framework.",
        ["Observability", "Security", "Operational Excellence", "Portability", "Gamification"],
        [1,2],
        "Security and Operational Excellence are two of the six pillars (also Reliability, Performance Efficiency, Cost Optimization, Sustainability)."
    )); idc += 1

    q.append(make_mcq(
        idc, "Cloud Concepts",
        "Which AWS global infrastructure component is a collection of data centers within a Region?",
        ["Edge location", "Availability Zone", "Local Zone", "Wavelength Zone"],
        1,
        "An Availability Zone (AZ) is one or more discrete data centers within a Region."
    )); idc += 1

    # Programmatic variants
    benefits = [
        ("faster experimentation and reduced time-to-market", "agility"),
        ("adding and removing capacity automatically", "elasticity"),
        ("serving users from locations closer to them", "lower latency via global reach"),
        ("avoiding over-provisioning for peak", "right-sizing / elasticity"),
    ]
    wrongs = ["manual capacity planning", "monolithic deployments", "on-prem fixed CapEx", "single-AZ design"]
    for (text, keyword) in benefits:
        opts = ["Global reach", "Pay-as-you-go", "Elasticity", "Agility"]
        # Map keyword to the correct index in opts
        if "elastic" in keyword:
            correct_idx = 2
        elif "pay" in keyword or "CapEx" in keyword:
            correct_idx = 1
        elif "global" in keyword or "latency" in keyword:
            correct_idx = 0
        elif "agility" in keyword or "experiment" in keyword:
            correct_idx = 3
        else:
            correct_idx = 1
        q.append(make_mcq(
            idc, "Cloud Concepts",
            f"Which benefit of cloud computing MOST helps with {text}?",
            opts,
            correct_idx,
            "Match the benefit to the scenario: agility speeds experimentation, elasticity handles dynamic capacity needs, pay-as-you-go avoids CapEx, and global reach reduces latency.",
        )); idc += 1

    # Multi-response: pick 2 cloud benefits
    cloud_benefit_sets = [
        (["Agility", "CapEx commitment", "Elasticity", "Vendor lock-in", "Manual scaling"], {0,2}),
        (["High availability", "Manual procurement", "Global footprint", "Long hardware lead time", "Tape backups"], {0,2}),
    ]
    for opts, ans in cloud_benefit_sets:
        q.append(make_mrq(
            idc, "Cloud Concepts",
            "Which TWO are benefits commonly associated with AWS Cloud?",
            opts, sorted(list(ans)),
            "Agility, elasticity, HA, and global reach are key cloud benefits."
        )); idc += 1

    # Fill up to 'need' with randomized but safe knowledge checks
    while len(q) < need:
        choice = rng.choice(["well_arch", "global", "economics"])
        if choice == "well_arch":
            pillars = ["Security","Reliability","Performance Efficiency","Cost Optimization","Sustainability","Operational Excellence"]
            wrong = ["Portability","User Experience","Refactoring","Latency budget"]
            opts = rng.sample(pillars, 2) + rng.sample(wrong, 2)
            rng.shuffle(opts)
            correct = {opts.index(p) for p in opts if p in pillars}
            # make it MCQ by picking one pillar intentionally
            correct_single = list(correct)[0]
            q.append(make_mcq(
                idc, "Cloud Concepts",
                "Which option is a pillar of the AWS Well-Architected Framework?",
                opts,
                correct_single,
                "The six pillars are: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability."
            ))
            idc += 1
        elif choice == "global":
            opts = ["Region", "Availability Zone", "Edge location", "Data rack"]
            q.append(make_mcq(
                idc, "Cloud Concepts",
                "Which option is used by Amazon CloudFront to cache content closer to users?",
                opts, 2,
                "CloudFront uses edge locations to cache content at the network edge."
            )); idc += 1
        else:
            q.append(make_mcq(
                idc, "Cloud Concepts",
                "Which cost concept lets you pay only for what you use without long-term contracts?",
                ["Reserved Instances", "Savings Plans", "Pay-as-you-go", "Dedicated Hosts"],
                2,
                "Pay-as-you-go is the on-demand, consumption-based model."
            )); idc += 1

    return q[:need]

def sec_comp_templates(start_id: int, need: int, rng: random.Random) -> List[Question]:
    """Security & Compliance question generator."""
    q: List[Question] = []
    idc = start_id

    # Static core items
    q.append(make_mcq(
        idc, "Security & Compliance",
        "Under the AWS shared responsibility model, who is responsible for patching the hypervisor?",
        ["Customer", "AWS", "Third-party auditor", "Managed Service Provider"],
        1,
        "AWS secures the infrastructure that runs the services; customers secure what they put in the cloud."
    )); idc += 1

    q.append(make_mcq(
        idc, "Security & Compliance",
        "Which control is stateful and operates at the instance level?",
        ["Network ACL", "Security group", "IAM policy", "WAF rule"],
        1,
        "Security groups are stateful, attached to ENIs/instances; NACLs are stateless."
    )); idc += 1

    q.append(make_mrq(
        idc, "Security & Compliance",
        "Select TWO recommended IAM best practices.",
        ["Use long-lived access keys in code", "Enable MFA for sensitive accounts",
         "Grant least privilege", "Share root credentials for collaboration", "Rotate credentials regularly"],
        [1,2],
        "Enable MFA and follow least-privilege; avoid embedding long-lived keys or using the root user."
    )); idc += 1

    q.append(make_mcq(
        idc, "Security & Compliance",
        "Which service records API activity across your AWS account(s)?",
        ["Amazon CloudWatch", "AWS CloudTrail", "AWS Config", "Amazon GuardDuty"],
        1,
        "CloudTrail records account API activity; CloudWatch is metrics/logs; Config tracks configuration state; GuardDuty is threat detection."
    )); idc += 1

    # Variants: shared responsibility prompts
    items = [
        ("encryption of data IN transit for your applications", "Customer"),
        ("physical security of data centers", "AWS"),
        ("patching guest OS on Amazon EC2", "Customer"),
        ("availability of Managed Services infrastructure", "AWS"),
    ]
    for text, owner in items:
        opts = ["Customer","AWS","Both share","No one"]
        correct = opts.index("Customer" if owner=="Customer" else "AWS" if owner=="AWS" else "Both share")
        q.append(make_mcq(
            idc, "Security & Compliance",
            f"Under shared responsibility, who is responsible for {text}?",
            opts, correct,
            "AWS secures the cloud; you secure what you run IN the cloud. Some areas are shared (e.g., certain encryption responsibilities)."
        )); idc += 1

    # Multi-response: pick two detective controls
    q.append(make_mrq(
        idc, "Security & Compliance",
        "Which TWO are primarily detective controls?",
        ["AWS CloudTrail", "AWS Shield Advanced", "Amazon CloudWatch Alarms", "AWS WAF", "AWS KMS"],
        [0,2],
        "CloudTrail and CloudWatch Alarms detect/report events. Shield/WAF are protective; KMS manages encryption keys."
    )); idc += 1

    # Fill up to 'need'
    while len(q) < need:
        choice = rng.choice(["iam", "network", "compliance"])
        if choice == "iam":
            q.append(make_mcq(
                idc, "Security & Compliance",
                "Which IAM entity should an application assume to obtain temporary credentials securely?",
                ["IAM user with long-lived keys", "IAM role", "Root user", "Group"],
                1,
                "Use IAM roles to provide temporary credentials via STS."
            )); idc += 1
        elif choice == "network":
            q.append(make_mcq(
                idc, "Security & Compliance",
                "Which option blocks or allows traffic at the subnet boundary and is stateless?",
                ["Security group", "NACL", "VPC endpoint policy", "Route table"],
                1,
                "Network ACLs are stateless and operate at the subnet boundary."
            )); idc += 1
        else:
            q.append(make_mcq(
                idc, "Security & Compliance",
                "Where can you download AWS compliance reports (e.g., SOC) for your auditors?",
                ["AWS Artifact", "AWS Organizations", "AWS Secrets Manager", "AWS License Manager"],
                0,
                "AWS Artifact provides on-demand access to AWS compliance reports and agreements."
            )); idc += 1

    return q[:need]

def tech_services_templates(start_id: int, need: int, rng: random.Random) -> List[Question]:
    """Cloud Technology & Services question generator."""
    q: List[Question] = []
    idc = start_id

    # Static core
    q.append(make_mcq(
        idc, "Cloud Tech & Services",
        "Which service is serverless compute that runs code in response to events?",
        ["Amazon EC2", "AWS Lambda", "Amazon ECS on EC2", "Amazon Lightsail"],
        1,
        "AWS Lambda is serverless function compute; no server management."
    )); idc += 1

    q.append(make_mrq(
        idc, "Cloud Tech & Services",
        "Select TWO services that are considered GLOBAL (not strictly Regional).",
        ["Amazon VPC", "Amazon S3", "Amazon Route 53", "AWS Identity and Access Management (IAM)", "Amazon EBS"],
        [2,3],
        "Route 53 and IAM are global services."
    )); idc += 1

    q.append(make_mcq(
        idc, "Cloud Tech & Services",
        "Which storage option is object storage designed for high durability and virtually unlimited scale?",
        ["Amazon EBS", "Amazon EFS", "Amazon S3", "AWS Storage Gateway"],
        2,
        "Amazon S3 is object storage with high durability and virtually unlimited scale."
    )); idc += 1

    q.append(make_mcq(
        idc, "Cloud Tech & Services",
        "You need a fully managed relational database engine. Which is the BEST fit?",
        ["Amazon DynamoDB", "Amazon RDS", "Amazon Redshift", "Amazon OpenSearch Service"],
        1,
        "Amazon RDS is a managed relational database service."
    )); idc += 1

    # Parametric scenarios: compute choices
    compute_scenarios = [
        ("run containers without managing servers", ["Amazon ECS on EC2","AWS Fargate","Amazon EKS","Amazon EMR"], 1,
         "Fargate runs containers without managing servers."),
        ("access VMs with max control over OS and networking", ["AWS Lambda","Amazon Lightsail","Amazon EC2","AWS Batch"], 2,
         "EC2 provides granular control over instances and OS."),
        ("simple VPS for blogs or small apps", ["Amazon Lightsail","Amazon EKS","AWS Glue","Amazon MQ"], 0,
         "Lightsail is simplified VPS hosting for small workloads."),
    ]
    for text, opts, correct_idx, expl in compute_scenarios:
        q.append(make_mcq(
            idc, "Cloud Tech & Services",
            f"Which is the BEST choice to {text}?",
            opts, correct_idx, expl
        )); idc += 1

    # Storage class selection variants
    s3_variants = [
        ("infrequently accessed data that must be immediately retrievable", ["S3 Standard-IA","S3 One Zone-IA","S3 Glacier Flexible Retrieval","S3 Glacier Deep Archive"], 0,
         "Standard-IA is for infrequent access with milliseconds retrieval across multiple AZs."),
        ("archival data with the lowest storage cost and hours retrieval time", ["S3 Standard","S3 Glacier Instant Retrieval","S3 Glacier Deep Archive","S3 Intelligent-Tiering"], 2,
         "Deep Archive offers the lowest cost with retrieval in hours."),
        ("unknown/variable access patterns and you want auto-tiering", ["S3 Intelligent-Tiering","S3 Standard","S3 One Zone-IA","S3 Glacier Flexible Retrieval"], 0,
         "Intelligent-Tiering optimizes cost by auto-moving objects between tiers.")
    ]
    for text, opts, idx, expl in s3_variants:
        q.append(make_mcq(
            idc, "Cloud Tech & Services",
            f"Which S3 storage class fits {text}?",
            opts, idx, expl
        )); idc += 1

    # Messaging & integration
    q.append(make_mcq(
        idc, "Cloud Tech & Services",
        "Which service provides queueing to decouple microservices?",
        ["Amazon SNS", "Amazon SQS", "Amazon EventBridge", "AWS Step Functions"],
        1,
        "SQS is a fully managed message queue to decouple components."
    )); idc += 1

    q.append(make_mcq(
        idc, "Cloud Tech & Services",
        "Which service is a pub/sub notification service (fan-out)?",
        ["Amazon SQS", "Amazon SNS", "AWS Step Functions", "Amazon MQ"],
        1,
        "SNS is a pub/sub notification service; SQS is queueing."
    )); idc += 1

    # Fill up to 'need'
    while len(q) < need:
        choice = rng.choice(["db", "net", "monitor"])
        if choice == "db":
            q.append(make_mcq(
                idc, "Cloud Tech & Services",
                "Which database service offers single-digit millisecond latency at any scale and is key-value / document?",
                ["Amazon Aurora", "Amazon DynamoDB", "Amazon Redshift", "Amazon RDS for Oracle"],
                1,
                "DynamoDB is a serverless NoSQL database with single-digit ms latency."
            )); idc += 1
        elif choice == "net":
            q.append(make_mcq(
                idc, "Cloud Tech & Services",
                "Which feature enables private connectivity between a VPC and AWS services without using an Internet Gateway?",
                ["VPC peering", "AWS Direct Connect", "VPC endpoints", "NAT Gateway"],
                2,
                "VPC endpoints provide private connectivity to supported AWS services."
            )); idc += 1
        else:
            q.append(make_mcq(
                idc, "Cloud Tech & Services",
                "Which service is primarily used for metrics and alarms?",
                ["AWS CloudTrail", "Amazon CloudWatch", "AWS Config", "AWS Audit Manager"],
                1,
                "CloudWatch collects metrics/logs and supports alarms; CloudTrail is for API auditing."
            )); idc += 1

    return q[:need]

def billing_templates(start_id: int, need: int, rng: random.Random) -> List[Question]:
    """Billing, Pricing & Support generator."""
    q: List[Question] = []
    idc = start_id

    q.append(make_mcq(
        idc, "Billing, Pricing & Support",
        "Which tool helps you visualize and analyze AWS spend over time?",
        ["AWS TCO Calculator", "AWS Pricing Calculator", "AWS Cost Explorer", "AWS Budgets"],
        2,
        "Cost Explorer analyzes/spots trends in historical/forecasted spend."
    )); idc += 1

    q.append(make_mcq(
        idc, "Billing, Pricing & Support",
        "Which feature lets you set thresholds and receive alerts when costs exceed targets?",
        ["AWS Cost Explorer", "AWS Budgets", "AWS Organizations", "AWS Billing Conductor"],
        1,
        "AWS Budgets lets you set cost/usage thresholds and alerts."
    )); idc += 1

    q.append(make_mcq(
        idc, "Billing, Pricing & Support",
        "Which option typically offers the LOWEST compute price for fault-tolerant, flexible workloads?",
        ["On-Demand Instances", "Savings Plans", "Spot Instances", "Dedicated Hosts"],
        2,
        "Spot Instances offer steep discounts for interruption-tolerant workloads."
    )); idc += 1

    q.append(make_mrq(
        idc, "Billing, Pricing & Support",
        "Select TWO features of the AWS Business Support plan.",
        ["24x7 access to Cloud Support engineers", "Technical Account Manager (TAM) included",
         "Trusted Advisor full checks", "Response times only during business hours", "Architected guidance via TAM only"],
        [0,2],
        "Business includes 24x7 support and full Trusted Advisor checks; a dedicated TAM is part of Enterprise tiers."
    )); idc += 1

    # Parametric savings questions
    scenarios = [
        ("steady, predictable 24x7 workload for a year", ["On-Demand","Savings Plans","Spot","Dedicated Hosts"], 1,
         "Compute Savings Plans or RIs (conceptually) suit steady usage; they offer committed-use discounts."),
        ("batch jobs that can be interrupted and rescheduled", ["Savings Plans","Spot Instances","Dedicated Hosts","On-Demand"], 1,
         "Spot is ideal for interruption-tolerant, flexible start/stop workloads."),
        ("unpredictable short-lived spikes", ["Spot","On-Demand","Savings Plans","Dedicated Hosts"], 1,
         "On-Demand fits spiky, unpredictable usage without commitment.")
    ]
    for text, opts, idx, expl in scenarios:
        q.append(make_mcq(
            idc, "Billing, Pricing & Support",
            f"Which purchasing model is MOST cost-effective for {text}?",
            opts, idx, expl
        )); idc += 1

    # Organizations & consolidated billing
    q.append(make_mcq(
        idc, "Billing, Pricing & Support",
        "Which AWS service provides consolidated billing across multiple AWS accounts?",
        ["AWS Control Tower", "AWS Organizations", "AWS Billing Conductor", "AWS License Manager"],
        1,
        "AWS Organizations offers consolidated billing and account management."
    )); idc += 1

    # Fill up to 'need'
    support_situations = [
        ("need guidance reviewing architecture for production launch", ["Developer","Business","Enterprise On-Ramp","Enterprise"], 1,
         "Business includes architectural guidance and faster response; Enterprise tiers add TAM and more."),
        ("mission-critical workload requiring a designated TAM", ["Developer","Business","Enterprise On-Ramp","Enterprise"], 3,
         "Enterprise includes a TAM; Enterprise On-Ramp offers TAM-like engagement for critical workloads (but not full Enterprise)."),
    ]
    i = 0
    while len(q) < need:
        if i < len(support_situations):
            text, opts, idx, expl = support_situations[i]
            q.append(make_mcq(
                idc, "Billing, Pricing & Support",
                f"Which support plan is MOST appropriate if you {text}?",
                opts, idx, expl
            )); idc += 1
            i += 1
        else:
            choice = rng.choice(["pricing_calc", "budgets"])
            if choice == "pricing_calc":
                q.append(make_mcq(
                    idc, "Billing, Pricing & Support",
                    "Which tool estimates costs BEFORE you deploy resources?",
                    ["AWS Pricing Calculator", "AWS Cost Explorer", "AWS Budgets", "AWS Trusted Advisor"],
                    0,
                    "Use the AWS Pricing Calculator to estimate costs pre-deployment."
                )); idc += 1
            else:
                q.append(make_mcq(
                    idc, "Billing, Pricing & Support",
                    "Which service provides proactive checks for cost optimization, performance, security, fault tolerance, and service quotas?",
                    ["AWS Inspector", "AWS Trusted Advisor", "AWS Compute Optimizer", "AWS Systems Manager"],
                    1,
                    "Trusted Advisor runs best-practice checks across multiple categories."
                )); idc += 1

    return q[:need]

# -----------------------------
# Build the full 150-question set (weighted)
# -----------------------------
def build_questions(total: int, seed: int = 42) -> List[Question]:
    rng = random.Random(seed)

    # Compute target counts from weights
    counts = {
        "Cloud Concepts": round(total * DOMAINS["Cloud Concepts"]),
        "Security & Compliance": round(total * DOMAINS["Security & Compliance"]),
        "Cloud Tech & Services": round(total * DOMAINS["Cloud Tech & Services"]),
        "Billing, Pricing & Support": total  # finalize after
    }
    used = counts["Cloud Concepts"] + counts["Security & Compliance"] + counts["Cloud Tech & Services"]
    counts["Billing, Pricing & Support"] = total - used  # ensure exact total 150

    # Generate per-domain
    idc = 1
    cc = cc_concepts_templates(idc, counts["Cloud Concepts"], rng); idc += len(cc)
    sc = sec_comp_templates(idc, counts["Security & Compliance"], rng); idc += len(sc)
    ts = tech_services_templates(idc, counts["Cloud Tech & Services"], rng); idc += len(ts)
    bp = billing_templates(idc, counts["Billing, Pricing & Support"], rng); idc += len(bp)

    all_q = cc + sc + ts + bp
    rng.shuffle(all_q)
    # Enforce exam-like counts: MCQ w/ 4 options, MRQ w/ 5 options
    normalized = []
    for q in all_q:
        if q.multi and len(q.options) < 5:
            # Add safe distractors
            extras = ["Not applicable", "All of the above", "None of the above", "Use a third-party tool", "Refactor the app"]
            needed = 5 - len(q.options)
            add = rng.sample(extras, needed)
            q.options = q.options + add
            if q.option_explanations is not None:
                q.option_explanations = (q.option_explanations or []) + ["Distractor" for _ in add]
        if not q.multi and len(q.options) != 4:
            # Clamp/expand to 4 for consistency
            if len(q.options) > 4:
                # Keep the correct one plus three random wrongs
                correct_idx = list(q.correct)[0]
                correct_opt = q.options[correct_idx]
                wrongs = [o for i,o in enumerate(q.options) if i != correct_idx]
                chosen_wrongs = rng.sample(wrongs, 3)
                new_opts = [correct_opt] + chosen_wrongs
                rng.shuffle(new_opts)
                # Reorder per-option explanations in lockstep
                if q.option_explanations is not None and len(q.option_explanations) == len(q.options):
                    correct_expl = q.option_explanations[correct_idx]
                    wrong_expls = [e for i,e in enumerate(q.option_explanations) if i != correct_idx]
                    # Align wrong explanations with chosen_wrongs order
                    chosen_expls = []
                    for w in chosen_wrongs:
                        idx = wrongs.index(w)
                        chosen_expls.append(wrong_expls[idx])
                    new_expls = [correct_expl] + chosen_expls
                    # Shuffle explanations to match new_opts order
                    mapping = {opt: expl for opt, expl in zip([correct_opt] + chosen_wrongs, new_expls)}
                    q.option_explanations = [mapping[o] for o in new_opts]
                q.correct = {new_opts.index(correct_opt)}
                q.options = new_opts
            else:
                while len(q.options) < 4:
                    q.options.append("None of the above")
                    if q.option_explanations is not None:
                        q.option_explanations.append("Distractor")
        normalized.append(q)

    # De-duplicate by prompt within a session to avoid repeats
    seen = set()
    deduped: List[Question] = []
    for q in normalized:
        key = f"{q.domain}|{q.prompt.strip()}|{'MRQ' if q.multi else 'MCQ'}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(q)
    rng.shuffle(deduped)
    return deduped[:total]

# -----------------------------
# Session state
# -----------------------------
# Initialize authentication state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "questions" not in st.session_state:
    st.session_state.questions = build_questions(TOTAL_QUESTIONS, seed=42)
    st.session_state.index = 0
    st.session_state.correct_count = 0
    st.session_state.answered = {}          # question_id -> user selection set
    st.session_state.per_domain = {}        # domain -> (correct, total_seen)
    st.session_state.show_feedback = False
    st.session_state.finished = False

def reset_quiz(total_override: Optional[int] = None, seed: Optional[int] = None):
    total = total_override if total_override is not None else st.session_state.get("desired_total", TOTAL_QUESTIONS)
    use_seed = seed if seed is not None else random.randint(0, 10_000)
    st.session_state.questions = build_questions(total, seed=use_seed)
    st.session_state.index = 0
    st.session_state.correct_count = 0
    st.session_state.answered = {}
    st.session_state.per_domain = {}
    st.session_state.show_feedback = False
    st.session_state.finished = False

# -----------------------------
# Password Protection
# -----------------------------
# Use Streamlit secrets for secure password storage
# For local development, you can set a default password
try:
    PASSWORD = st.secrets["password"]
except:
    PASSWORD = "aws2025"  # Fallback for local development only

if not st.session_state.authenticated:
    st.title("CCP Practice Exam")
    st.write("Please enter the password to access the quiz.")
    
    password_input = st.text_input("Password:", type="password", key="password_field")
    
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("Login", use_container_width=True):
            if password_input == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")
    
    st.stop()  # Prevent the rest of the app from running

# -----------------------------
# Header & Info
# -----------------------------
inject_css()
st.title("AWS Certified Cloud Practitioner (CLF-C02) — 150-Question Practice Exam")
st.caption("Format mirrors AWS exam: MCQ (1 of 4) and MRQ (≥2 of ≥5). Scoring shown as a 100–1000 scaled estimate; pass at 700+")

with st.expander("About format & scoring (from AWS)"):
    st.markdown("- Multiple-choice & multiple-response; 65 total on the real exam (50 scored + 15 unscored). No penalty for guessing.")
    st.markdown("- Scaled scoring **100–1000**, passing **700**; compensatory model (pass overall).")
    st.markdown("This app uses a linear approximation to calculate a scaled score for practice purposes.")

st.sidebar.header("Controls")
desired_total = st.sidebar.number_input("Number of questions", min_value=10, max_value=150, value=min(TOTAL_QUESTIONS, 65), step=5)
st.session_state.desired_total = int(desired_total)
seed_val = st.sidebar.number_input("Randomization seed", value=42, step=1)
if st.sidebar.button("Start Over (new set)"):
    reset_quiz(total_override=int(desired_total), seed=int(seed_val))

# -----------------------------
# Main quiz flow
# -----------------------------
qs: List[Question] = st.session_state.questions
idx = st.session_state.index
finished = st.session_state.finished

def record_domain(q: Question, got_it: bool):
    dom = q.domain
    c,t = st.session_state.per_domain.get(dom, (0,0))
    st.session_state.per_domain[dom] = (c + (1 if got_it else 0), t + 1)

if not finished and idx < len(qs):
    q = qs[idx]
    st.subheader(f"Question {idx+1} of {len(qs)}")
    # Progress + domain
    st.progress(idx / len(qs))
    st.markdown(f"<span class=\"pill\">{q.domain}</span>", unsafe_allow_html=True)
    prompt = q.prompt + (f"  \n**Select {len(q.correct)}.**" if q.multi else "")
    st.write(prompt)

    already_answered = (q.id in st.session_state.answered)

    if q.multi:
        # Multi-response: checkboxes
        selections = []
        for i,opt in enumerate(q.options):
            if st.checkbox(opt, key=f"chk-{q.id}-{i}", disabled=already_answered):
                selections.append(i)
    else:
        # MCQ: radio buttons
        choice = st.radio("Please choose one:", q.options, index=None, key=f"rad-{q.id}", disabled=already_answered)
        selections = [] if choice is None else [q.options.index(choice)]

    # Precompute selection set and validity for this question
    sel_set = set(selections)
    valid_selection = (len(sel_set) == len(q.correct)) if q.multi else (len(sel_set) == 1)

    col1, col2, col3 = st.columns([1,1,1])
    submitted = col1.button("Submit answer", use_container_width=True, disabled=already_answered)
    # Next enabled once answered
    next_disabled = not already_answered
    nextq = col2.button("Next Question", use_container_width=True, disabled=next_disabled)
    finish_now = col3.button("Finish Quiz", use_container_width=True)

    if submitted:
        if q.multi and not valid_selection:
            st.warning(f"Select exactly {len(q.correct)} option(s) before submitting.")
        elif not q.multi and not valid_selection:
            st.warning("Please select one option before submitting.")
        else:
            st.session_state.answered[q.id] = sel_set
            is_correct = (sel_set == q.correct)
            if is_correct:
                st.session_state.correct_count += 1
            record_domain(q, is_correct)
            # Rerun to immediately reflect disabled submit and enabled next, and show feedback
            st.rerun()

    # If already answered, display feedback and explanations
    if already_answered:
        ans_set = st.session_state.answered[q.id]
        correct_now = (ans_set == q.correct)
        st.markdown("-" * 30)
        st.write(f"**{'Correct!' if correct_now else 'Not quite.'}**")
        corr_labels = [q.options[i] for i in sorted(list(q.correct))]
        st.markdown(f"<div class='answer-row'><strong>Answer:</strong> {', '.join(corr_labels)}</div>", unsafe_allow_html=True)
        st.info(q.explanation)

        st.markdown("**Answer breakdown**")
        for i, opt in enumerate(q.options):
            mark = "(Correct)" if i in q.correct else "(Incorrect)"
            if q.option_explanations and len(q.option_explanations) == len(q.options):
                expl = q.option_explanations[i]
            else:
                base = describe_option(opt)
                if i in q.correct:
                    expl = q.explanation or base
                else:
                    suffix = " - Not the best fit for this scenario." if base else "Not the best fit for this scenario."
                    expl = (base + suffix) if base else suffix
            st.write(f"- {mark} {opt}: {expl}")

    if nextq and (q.id in st.session_state.answered):
        st.session_state.index += 1
        # clear checkbox/radio selections between questions by regenerating
        st.rerun()

    if finish_now:
        st.session_state.finished = True
        st.rerun()

else:
    st.session_state.finished = True

# -----------------------------
# Results
# -----------------------------
if st.session_state.finished:
    total_answered = len(st.session_state.answered)
    raw = st.session_state.correct_count
    # If user ended early, only count what was answered but scale to total attempted
    total_for_score = total_answered if total_answered > 0 else len(st.session_state.questions)
    scaled = raw_to_scaled(raw, total_for_score)
    passed = scaled >= 700

    st.header("Final Results")
    st.metric(label="Scaled Score (estimate)", value=f"{scaled} / 1000")
    st.metric(label="Status", value=("PASSED" if passed else "FAILED"))
    st.write(f"Answered: **{total_answered}** / {len(st.session_state.questions)}  •  Correct: **{raw}**")

    # Domain breakdown
    st.subheader("Domain breakdown")
    for dom, (c,t) in st.session_state.per_domain.items():
        pct = (c/t*100) if t else 0.0
        st.write(f"- **{dom}**: {c}/{t} correct ({pct:.1f}%)")

    st.divider()
    if st.button("Retake (apply settings)"):
        reset_quiz(total_override=int(st.session_state.get("desired_total", TOTAL_QUESTIONS)), seed=int(seed_val))
        st.experimental_rerun()

