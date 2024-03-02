# Automating AWS Infrastructure with Boto3

This project includes the automation of AWS infrastructure setup using Boto3, which includes provisioning and managing resources such as EC2 instances, S3 buckets, SNS topics, Lambda functions, Application Load Balancers (ALB), and Auto Scaling Groups (ASG). 

## Prerequisites

- AWS Command Line Interface (CLI) configured with AWS region, access key and secret key in the config and credentials files located in the .aws folder
- Python 3.10 and above
- Boto3 library (`pip install boto3`) on command line

## AWS Components Automation

### EC2 Instances

This function is to initialize the EC2 Instances using linux scripts on Ubuntu 22.04 AMI. 

```python
ec2_client = boto3.client('ec2')
# Launch EC2 instance
instance_id = launch_ec2_instance('my-app-instance', user_data_script)
```

# S3 Bucket

This is to initialize a bucket for ASG logging etc.

```python
s3_client = boto3.client('s3')
bucket_name = 'my-app-logs'

def create_bucket(name):
    # Assume implementation

create_bucket(bucket_name)
```
## SNS Topics for Alerts

SNS topics for different alert types are created, and administrators are subscribed through SMS and email. I used a simple SNS arrangement

```python
import boto3

sns_client = boto3.client('sns')
topic_arn = sns_client.create_topic(Name='HealthAlerts')['TopicArn']
sns_client.subscribe(TopicArn=topic_arn, Protocol='email', Endpoint='admin@example.com')
```
# Lambda Health Check

This function is to assess instance health

```python
lambda_client = boto3.client('lambda')

def lambda_health_check_handler(event, context):
    # Lambda function code here
```
# Application Load Balancer (ALB)

An ALB is deployed to balance traffic between frontend and backend, with access logging enabled and stored in the specified S3 bucket.

```python
import boto3

elbv2_client = boto3.client('elbv2')

def deploy_alb_and_register_instances(frontend_instance_id, backend_instance_id, vpc_id, bucket_name):
    # Assume implementation

alb_arn = deploy_alb_and_register_instances(frontend_instance_id, backend_instance_id, 'vpc-xxxx', bucket_name)

```

# Auto Scaling Group (ASG)

For automatic scaling of the load

## Python Script

```python
import boto3

asg_client = boto3.client('autoscaling')

def create_asg(name, launch_configuration_name):
    # Assume implementation

create_asg('my-app-asg', launch_configuration_name)
```
# Setup Steps
Things that need to be replaced in the code

### General AWS Resource Identifiers and Configuration Details:

- **Region Identifier**: Replace `eu-west-2` with the AWS region in which you are deploying your resources. (Line numbers: Various, including but not limited to lines 8, 14, 20, etc.)
- **Account ID**: Replace `xxxxxxxxxxxxx` in ARNs with your AWS account ID. (e.g., Line 13 for `target_group_arn`, Line 14 for `sns_topic_arn`)

### EC2 Configuration:

- **AMI ID (`ami-xxxxxxxxxxxx`)**: Choose an AMI that is compatible with your application requirements. This can be found in the EC2 Dashboard under "AMIs." (Lines 106, 128)
- **VPC ID (`vpc-xxxxxxxxxxxxx`)**: The ID of the VPC where you want to deploy your resources. Found in the VPC Dashboard. (Line 84)
- **Subnet IDs (`subnet-xxxxxxxxxxxxx`)**: The IDs of the subnets for deploying the EC2 instances and ALB. Found in the VPC Dashboard under "Subnets." (Lines 85, 196, 250)
- **Key Pair Name (`xxxxxxxxxxxxx`)**: The name of the EC2 Key Pair for SSH access to the instances. Found or created in the EC2 Dashboard under "Key Pairs." (Line 86)
- **Security Group ID (`sg-xxxxxxxxxxxx`)**: The ID of the Security Group to associate with the EC2 instances and ALB. Found in the EC2 Dashboard under "Security Groups." (Lines 104, 195)

### S3 Configuration:

- **Bucket Name (`xxxxxxxxxxxxx`)**: Choose a globally unique name for the S3 bucket. (Lines 72, 191)

### Elastic Load Balancing (ELB) Configuration:

- **Target Group ARN**: After creating a target group in the ELB service, replace `arn:aws:elasticloadbalancing:eu-west-2:xxxxxxxxxxxx:targetgroup/xxxxxxxxxxxxx/xxxxxxxxxxxxx` with the actual ARN. (Lines 13, 206)

### Simple Notification Service (SNS) Configuration:

- **SNS Topic ARN**: After creating an SNS topic, replace `arn:aws:sns:eu-west-2:xxxxxxxxxxxxx:xxxxxxxxxxxxx.fifo` with the actual ARN. (Line 14)

### Auto Scaling Configuration:

- **Launch Configuration Names**: Provide unique names for the launch configurations for frontend and backend instances. (Lines 232, 239)
- **Auto Scaling Group Name**: Provide a name for the Auto Scaling Group. (Line 250)

### Additional Details:

- **Phone Numbers (`+91xxxxxxxxxx`)**: Replace with actual phone numbers to subscribe to SMS notifications. (Line 168)
- **Email Addresses (`example@gmail.com`)**: Replace with actual email addresses to subscribe to email notifications. (Line 173)

Ensure that you have the necessary permissions to create and manage these resources in your AWS account.



