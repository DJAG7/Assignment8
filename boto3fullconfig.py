import boto3
import json 

# Initializing Boto3 Clients (AWS Configure and Credentials)
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
lambda_client = boto3.client('lambda') 
elbv2_client = boto3.client('elbv2')
asg_client= boto3.client('autoscaling')

# Lambda Health Check Configuration
    #
    #
    #

def lambda_health_check_handler(event, context):
    try:
        # Define ARNs for the target group and SNS topic
        target_group_arn = 'arn:aws:elasticloadbalancing:eu-west-2:xxxxxxxxxxxxx:targetgroup/xxxxxxxxxxxxx/xxxxxxxxxxxxx'
        sns_topic_arn = 'arn:aws:sns:eu-west-2:xxxxxxxxxxxxx:xxxxxxxxxxxxx.fifo'
        
        # Retrieve instance health status
        health_response = ec2_client.describe_instance_status()
        # Filter unhealthy instances (e.g., those in a 'stopped' state)
        unhealthy_instances = [instance for instance in health_response['InstanceStatuses'] if instance['InstanceState']['Name'] == 'stopped']
        
        # Process each unhealthy instance
        for instance in unhealthy_instances:
            instance_id = instance['InstanceId']
            # Create a snapshot for debugging purposes
            create_snapshot_response = ec2_client.create_snapshot(
                Description=f'Snapshot for debugging instance {instance_id}',
                InstanceId=instance_id,
            )
            # Terminate the unhealthy instance
            terminate_response = ec2_client.terminate_instances(InstanceIds=[instance_id])
            # Publish a notification about the terminated instance
            sns_message = {
                'InstanceID': instance_id,
                'Action': 'Terminated',
                'Reason': 'Health check failure',
                'SnapshotDetails': create_snapshot_response
            }
            sns_client.publish(
                TopicArn=sns_topic_arn,
                Message=json.dumps({'default': json.dumps(sns_message)}),
                Subject='Web Application Instance Failure Notification',
                MessageStructure='json'
            )
            print(f"Instance {instance_id} terminated and snapshot initiated for debugging. Notification sent.")
    except Exception as e:
        print(f"Error in lambda_health_check_handler: {str(e)}")

def create_bucket(bucket_name, region='eu-west-2'):

    try:
        location = {'LocationConstraint': region}
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print(f"Bucket {bucket_name} created.")
        # Bucket policy to allow ALB logs
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowSpecifiedActions",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:*",
                        "autoscaling-plans:*",
                        "ec2:*",
                        "elasticloadbalancing:*"
                    ],
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "StringEquals": {
                            "s3:x-amz-acl": "bucket-owner-full-control"
                        }
                    }
                },
                {
                    "Sid": "AllowALBLogsWrite",
                    "Effect": "Allow",
                    "Principal": {"Service": "elasticloadbalancing.amazonaws.com"},
                    "Action": "s3:PutObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/ALB-logs/*",
                    "Condition": {
                        "StringEquals": {
                            "s3:x-amz-acl": "bucket-owner-full-control"
                        }
                    }
                }
            ]
        }
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
        print(f"S3 bucket policy updated to allow ALB log delivery for {bucket_name}.")
    except Exception as e:
        print(f"Error in create_bucket: {str(e)}")

bucket_name = 'xxxxxxxxxxxxx'
create_bucket(bucket_name)


# EC2 Configuration
    #
    #
    #

# Specify your VPC, subnet, and key pair
vpc_id = 'vpc-xxxxxxxxxxxxx'
subnet_id = 'subnet-xxxxxxxxxxxxx'
key_pair_name = 'xxxxxxxxxxxxx'

# Common user data script for installing Nginx and cloning repository
common_user_data_script = """#!/bin/bash
sudo apt-get update -y
sudo apt-get install -y nginx
"""

# Additional backend setup, including Node.js installation and environment setup
backend_user_data_script = common_user_data_script + """
git clone https://github.com/xxxxxxxxxxxxx/xxxxxxxxxxxxx.git /var/www/html/xxxxxxxxxxxxx
curl -sL https
sudo apt-get install -y nodejs
cd /var/www/html/TravelMemory/backend
echo "MONGO_URI=mongodb+srv://testdb:hi@travelmemorydb.b3sfizx.mongodb.net/" > .env
echo "PORT=3000" >> .env
sudo npm install
sudo nohup npm start &
sudo systemctl start nginx
"""

# Frontend setup, including Node.js installation
frontend_user_data_script = common_user_data_script + """
git clone https://github.com/UnpredictablePrashant/TravelMemory.git /var/www/html/TravelMemory
curl -sL https://deb.nodesource.com/setup_current.x | sudo -E bash -
sudo apt-get install -y nodejs
cd /var/www/html/TravelMemory/frontend
sudo npm install
sudo nginx -t
sudo systemctl start nginx
sudo lsof -t -i tcp:80 -s tcp:listen | sudo xargs kill
sudo nohup npm start &
"""

# Using Security Group Already Configured
security_group_id = 'sg-xxxxxxxxxxxx'

# Launch EC2 instances for frontend and backend
def launch_ec2_instance(name_tag, user_data):
    
    instance = ec2_client.run_instances(
        ImageId='ami-xxxxxxxxxxxx',
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[security_group_id],  
        KeyName=key_pair_name,
        UserData=user_data,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': name_tag}],
        }],
        SubnetId=subnet_id
    )
    return instance['Instances'][0]['InstanceId']

# Launch ec2 function
frontend_instance_id = launch_ec2_instance('daniel-boto3-frontend', frontend_user_data_script)
backend_instance_id = launch_ec2_instance('daniel-boto3-backend', backend_user_data_script)
print("Frontend and backend instances launched successfully.")

# SNS Configuration

# Define SNS topics for different types of alerts
sns_topics = {
    'health_issues': 'HealthIssuesNotifications',
    'scaling_events': 'ScalingEventsNotifications',
    'high_traffic': 'HighTrafficNotifications'
}

# Create SNS topics and store their ARNs
sns_topic_arns = {}
for alert_type, topic_name in sns_topics.items():
    topic_response = sns_client.create_topic(Name=topic_name)
    sns_topic_arns[alert_type] = topic_response['TopicArn']
    print(f"SNS topic for {alert_type} created: {topic_response['TopicArn']}")

# Subscribe administrators to the SNS topics
administrators = {
    'sms_subscribers': ['+91xxxxxxxxxx'],  # Replace with actual phone numbers
    'email_subscribers': ['example@gmail.com']  # Replace with actual email addresses
}

for alert_type, topic_arn in sns_topic_arns.items():
    for phone_number in administrators['sms_subscribers']:
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='sms',
            Endpoint=phone_number
        )
        print(f"Subscribed {phone_number} to SMS notifications for {alert_type}.")
    
    for email_address in administrators['email_subscribers']:
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email_address
        )
        print(f"Subscribed {email_address} to email notifications for {alert_type}.")


# Function to create an Application Load Balancer and register EC2 instances
    #
    #
    #
    #

def deploy_alb_and_register_instances(frontend_instance_id, backend_instance_id, vpc_id, bucket_name):
    # Create an ALB with access logging enabled
    alb_response = elbv2_client.create_load_balancer(
        Name='DanielALB',
        Subnets=['subnet-xxxxxxxx', 'subnet-xxxxxxxx'],  # Replace with your subnet IDs
        SecurityGroups=[security_group_id],
        Scheme='internet-facing',
        Tags=[{'Key': 'Name', 'Value': 'DanielALB'}],
        IpAddressType='ipv4'
    )
    alb_arn = alb_response['LoadBalancers'][0]['LoadBalancerArn']
    print(f"ALB created with ARN: {alb_arn}")

    # Enable access logging for the ALB
    elbv2_client.modify_load_balancer_attributes(
        LoadBalancerArn=alb_arn,
        Attributes=[
            {
                'Key': 'access_logs.s3.enabled',
                'Value': 'true'
            },
            {
                'Key': 'access_logs.s3.bucket',
                'Value': bucket_name
            },
            {
                'Key': 'access_logs.s3.prefix',
                'Value': 'ALB-logs'
            }
        ]
    )
    print(f"Access logging for the ALB {alb_arn} enabled, logs will be stored in S3 bucket {bucket_name}.")

    # Target Group ARN
    target_group_arn = 'arn:aws:elasticloadbalancing:eu-west-2:xxxxxxxxxxxx:targetgroup/daniel-boto3/xxxxxxxxxxxx'
    
    # Register EC2 instances with the target group
    elbv2_client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[
            {'Id': frontend_instance_id, 'Port': 80},
            {'Id': backend_instance_id, 'Port': 3000}  # Assuming backend listens on port 3000
        ]
    )
    print(f"Instances {frontend_instance_id} and {backend_instance_id} registered to Target Group")

    # Create a listener for the ALB
    elbv2_client.create_listener(
        LoadBalancerArn=alb_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn}]
    )
    print("Listener created for ALB")

deploy_alb_and_register_instances(frontend_instance_id, backend_instance_id, vpc_id, bucket_name)


# ASG Config and AutoScaling
    #
    #
    #
    #

# Frontend Launch Configuration
asg_client.create_launch_configuration(
    LaunchConfigurationName='daniel-boto3-frontend-launch-configuration',
    ImageId='ami-xxxxxxxxxxxx',
    InstanceType='t2.micro',
    SecurityGroups=[security_group_id],
    KeyName=key_pair_name,
    UserData=frontend_user_data_script,
)

# Backend Launch Configuration
asg_client.create_launch_configuration(
    LaunchConfigurationName='daniel-boto3-backend-launch-configuration',
    ImageId='ami-xxxxxxxxxxxx',
    InstanceType='t2.micro',
    SecurityGroups=[security_group_id],
    KeyName=key_pair_name,
    UserData=backend_user_data_script,
)


#Defining Subnet IDs
subnet_ids=['subnet-xxxxxxxx', 'subnet-xxxxxxxx']


# Unified ASG for both Frontend and Backend
asg_client.create_auto_scaling_group(
    AutoScalingGroupName='daniel-boto3-asg',
    LaunchConfigurationName='daniel-boto3-frontend-launch-configuration',  
    MinSize=1,
    MaxSize=3,
    DesiredCapacity=2,
    TargetGroupARNs=['arn:aws:elasticloadbalancing:eu-west-2:xxxxxxxxxxxx:targetgroup/daniel-boto3/xxxxxxxxxxxx'],  
    VPCZoneIdentifier=subnet_ids,  
    Tags=[
        {'Key': 'Name', 'Value': 'daniel-boto3-unified-instance', 'PropagateAtLaunch': True},
        {'Key': 'Role', 'Value': 'frontend-backend', 'PropagateAtLaunch': True}  
    ]
)
