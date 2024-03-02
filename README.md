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

# Customization
Things that need to be replaced in the code-



