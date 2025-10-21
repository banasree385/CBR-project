# AWS Deployment Guide for AI Connect Website

This comprehensive guide provides step-by-step instructions for deploying the AI Connect website to Amazon Web Services (AWS).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Services Overview](#aws-services-overview)
3. [Deployment Methods](#deployment-methods)
4. [Method 1: AWS Elastic Beanstalk](#method-1-aws-elastic-beanstalk)
5. [Method 2: AWS ECS with Fargate](#method-2-aws-ecs-with-fargate)
6. [Method 3: AWS Lambda + S3](#method-3-aws-lambda--s3)
7. [Method 4: AWS EC2](#method-4-aws-ec2)
8. [Environment Configuration](#environment-configuration)
9. [Domain and SSL Setup](#domain-and-ssl-setup)
10. [CDN and Caching](#cdn-and-caching)
11. [Monitoring and Logging](#monitoring-and-logging)
12. [Security Configuration](#security-configuration)
13. [Backup and Recovery](#backup-and-recovery)
14. [Cost Optimization](#cost-optimization)
15. [Troubleshooting](#troubleshooting)

## Prerequisites

- AWS account with appropriate permissions
- AWS CLI installed and configured
- Node.js 16+ installed locally
- Docker installed (for containerized deployments)
- Git repository with the AI Connect project

### Install and Configure AWS CLI

```bash
# Install AWS CLI
# Windows: Download from AWS website
# macOS: brew install awscli
# Linux: apt-get install awscli

# Configure AWS CLI
aws configure
# Enter your Access Key ID, Secret Access Key, region, and output format
```

## AWS Services Overview

The AI Connect website can be deployed using various AWS services:

- **Elastic Beanstalk**: Easiest deployment with automatic scaling
- **ECS with Fargate**: Containerized deployment with full control
- **Lambda + API Gateway**: Serverless architecture
- **EC2**: Full virtual machine control
- **S3 + CloudFront**: Static hosting with CDN

## Deployment Methods

## Method 1: AWS Elastic Beanstalk

### Step 1: Prepare Application

Create `.ebextensions/01_nodecommand.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:container:nodejs:
    NodeCommand: "node backend/server.js"
  aws:elasticbeanstalk:application:environment:
    NODE_ENV: production
    PORT: 8081
```

Create `.platform/nginx/conf.d/proxy.conf`:

```nginx
upstream nodejs {
    server 127.0.0.1:8081;
    keepalive 256;
}

server {
    listen 80;

    if ($time_iso8601 ~ "^(\d{4})-(\d{2})-(\d{2})T(\d{2})") {
        set $year $1;
        set $month $2;
        set $day $3;
        set $hour $4;
    }
    access_log /var/log/nginx/healthd/application.log.$year-$month-$day-$hour healthd;
    access_log  /var/log/nginx/access.log  main;

    location / {
        proxy_pass  http://nodejs;
        proxy_set_header   Connection "";
        proxy_http_version 1.1;
        proxy_set_header        Host            $host;
        proxy_set_header        X-Real-IP       $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;
    }

    gzip on;
    gzip_comp_level 4;
    gzip_types
        text/plain
        text/css
        application/json
        application/javascript
        text/xml
        application/xml
        application/xml+rss
        text/javascript;
}
```

### Step 2: Initialize Elastic Beanstalk

```bash
# Initialize EB CLI
pip install awsebcli

# Initialize application
eb init ai-connect-app --region us-east-1 --platform node.js

# Create environment
eb create ai-connect-prod --envvars NODE_ENV=production,OPENAI_API_KEY=your-key
```

### Step 3: Deploy Application

```bash
# Deploy to Elastic Beanstalk
eb deploy

# Check status
eb status

# View logs
eb logs
```

### Step 4: Configure Environment Variables

```bash
# Set environment variables
eb setenv \
  NODE_ENV=production \
  OPENAI_API_KEY="your-openai-api-key" \
  EMAIL_SERVICE="gmail" \
  EMAIL_USER="your-email@gmail.com" \
  EMAIL_PASS="your-app-password" \
  CORS_ORIGIN="https://your-domain.com"
```

## Method 2: AWS ECS with Fargate

### Step 1: Create Dockerfile

```dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S aiconnect -u 1001

# Change ownership
RUN chown -R aiconnect:nodejs /app
USER aiconnect

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application
CMD ["node", "backend/server.js"]
```

### Step 2: Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository --repository-name ai-connect-app --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t ai-connect-app .
docker tag ai-connect-app:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-connect-app:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-connect-app:latest
```

### Step 3: Create ECS Task Definition

Create `task-definition.json`:

```json
{
  "family": "ai-connect-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "ai-connect-container",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-connect-app:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:ssm:us-east-1:<account-id>:parameter/ai-connect/openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-connect",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Step 4: Create ECS Cluster and Service

```bash
# Create cluster
aws ecs create-cluster --cluster-name ai-connect-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster ai-connect-cluster \
  --service-name ai-connect-service \
  --task-definition ai-connect-task:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:<account-id>:targetgroup/ai-connect-tg/12345,containerName=ai-connect-container,containerPort=3000
```

## Method 3: AWS Lambda + S3

### Step 1: Restructure for Serverless

Create `serverless.yml`:

```yaml
service: ai-connect-serverless

provider:
  name: aws
  runtime: nodejs18.x
  stage: prod
  region: us-east-1
  environment:
    NODE_ENV: production
    OPENAI_API_KEY: ${ssm:/ai-connect/openai-api-key}
    EMAIL_SERVICE: gmail
    EMAIL_USER: ${ssm:/ai-connect/email-user}
    EMAIL_PASS: ${ssm:/ai-connect/email-pass}

functions:
  api:
    handler: lambda.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
      - http:
          path: /
          method: ANY
          cors: true

plugins:
  - serverless-offline

custom:
  serverless-offline:
    httpPort: 3000
```

Create `lambda.js`:

```javascript
const serverless = require('serverless-http');
const app = require('./backend/server');

module.exports.handler = serverless(app);
```

### Step 2: Deploy with Serverless Framework

```bash
# Install Serverless Framework
npm install -g serverless

# Deploy
serverless deploy
```

### Step 3: Deploy Frontend to S3

```bash
# Create S3 bucket
aws s3 mb s3://ai-connect-frontend-bucket

# Enable static website hosting
aws s3 website s3://ai-connect-frontend-bucket \
  --index-document index.html \
  --error-document index.html

# Upload frontend files
aws s3 sync frontend/ s3://ai-connect-frontend-bucket --delete

# Set public read permissions
aws s3api put-bucket-policy --bucket ai-connect-frontend-bucket --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::ai-connect-frontend-bucket/*"
    }
  ]
}'
```

## Method 4: AWS EC2

### Step 1: Launch EC2 Instance

```bash
# Create key pair
aws ec2 create-key-pair --key-name ai-connect-key --query 'KeyMaterial' --output text > ai-connect-key.pem
chmod 400 ai-connect-key.pem

# Create security group
aws ec2 create-security-group \
  --group-name ai-connect-sg \
  --description "Security group for AI Connect application"

# Add rules to security group
aws ec2 authorize-security-group-ingress \
  --group-name ai-connect-sg \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name ai-connect-sg \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name ai-connect-sg \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --count 1 \
  --instance-type t3.micro \
  --key-name ai-connect-key \
  --security-groups ai-connect-sg \
  --user-data file://user-data.sh
```

### Step 2: Create User Data Script

Create `user-data.sh`:

```bash
#!/bin/bash
yum update -y
yum install -y git nodejs npm nginx

# Install PM2
npm install -g pm2

# Clone repository
cd /home/ec2-user
git clone https://github.com/your-username/ai-connect-website.git
cd ai-connect-website

# Install dependencies
npm install

# Create environment file
cat > .env << EOF
NODE_ENV=production
PORT=3000
OPENAI_API_KEY=your-openai-api-key
EMAIL_SERVICE=gmail
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
CORS_ORIGIN=https://your-domain.com
EOF

# Start application with PM2
pm2 start backend/server.js --name "ai-connect"
pm2 startup
pm2 save

# Configure Nginx
cat > /etc/nginx/conf.d/ai-connect.conf << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Start Nginx
systemctl start nginx
systemctl enable nginx
```

## Environment Configuration

### Using AWS Systems Manager Parameter Store

```bash
# Store sensitive environment variables
aws ssm put-parameter \
  --name "/ai-connect/openai-api-key" \
  --value "your-openai-api-key" \
  --type "SecureString"

aws ssm put-parameter \
  --name "/ai-connect/email-user" \
  --value "your-email@gmail.com" \
  --type "String"

aws ssm put-parameter \
  --name "/ai-connect/email-pass" \
  --value "your-app-password" \
  --type "SecureString"
```

### Using AWS Secrets Manager

```bash
# Create secret
aws secretsmanager create-secret \
  --name "ai-connect/app-secrets" \
  --description "Application secrets for AI Connect" \
  --secret-string '{
    "OPENAI_API_KEY": "your-openai-api-key",
    "EMAIL_USER": "your-email@gmail.com",
    "EMAIL_PASS": "your-app-password"
  }'
```

## Domain and SSL Setup

### Step 1: Configure Route 53

```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name your-domain.com \
  --caller-reference $(date +%s)

# Get name servers
aws route53 get-hosted-zone --id /hostedzone/Z123456789
```

### Step 2: Request SSL Certificate

```bash
# Request certificate
aws acm request-certificate \
  --domain-name your-domain.com \
  --subject-alternative-names www.your-domain.com \
  --validation-method DNS \
  --region us-east-1
```

### Step 3: Configure Application Load Balancer

```bash
# Create load balancer
aws elbv2 create-load-balancer \
  --name ai-connect-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-12345

# Create target group
aws elbv2 create-target-group \
  --name ai-connect-tg \
  --protocol HTTP \
  --port 3000 \
  --vpc-id vpc-12345 \
  --health-check-path /api/health

# Create HTTPS listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/ai-connect-alb/50dc6c495c0c9188 \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/ai-connect-tg/50dc6c495c0c9188
```

## CDN and Caching

### Create CloudFront Distribution

```bash
# Create CloudFront distribution
aws cloudfront create-distribution --distribution-config '{
  "CallerReference": "ai-connect-'$(date +%s)'",
  "Comment": "AI Connect CDN",
  "DefaultCacheBehavior": {
    "TargetOriginId": "ai-connect-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "MinTTL": 0,
    "ForwardedValues": {
      "QueryString": true,
      "Cookies": {
        "Forward": "none"
      }
    }
  },
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "ai-connect-origin",
        "DomainName": "your-alb-domain.us-east-1.elb.amazonaws.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only"
        }
      }
    ]
  },
  "Enabled": true,
  "PriceClass": "PriceClass_100"
}'
```

## Monitoring and Logging

### CloudWatch Configuration

```bash
# Create CloudWatch log group
aws logs create-log-group --log-group-name /aws/ai-connect/application

# Create custom metrics
aws cloudwatch put-metric-alarm \
  --alarm-name "AI-Connect-High-CPU" \
  --alarm-description "Alarm when CPU exceeds 70%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### Application Performance Monitoring

Add CloudWatch SDK to your application:

```javascript
// In your server.js
const AWS = require('aws-sdk');
const cloudwatch = new AWS.CloudWatch();

// Custom metric example
const putMetric = (metricName, value, unit = 'Count') => {
  const params = {
    Namespace: 'AI-Connect/Application',
    MetricData: [
      {
        MetricName: metricName,
        Value: value,
        Unit: unit,
        Timestamp: new Date()
      }
    ]
  };
  
  cloudwatch.putMetricData(params, (err, data) => {
    if (err) console.error('CloudWatch error:', err);
  });
};

// Track chatbot requests
app.use('/api/chatbot', (req, res, next) => {
  putMetric('ChatbotRequests', 1);
  next();
});
```

## Security Configuration

### WAF Configuration

```bash
# Create Web ACL
aws wafv2 create-web-acl \
  --name ai-connect-waf \
  --scope CLOUDFRONT \
  --default-action Allow={} \
  --rules '[
    {
      "Name": "RateLimitRule",
      "Priority": 1,
      "Statement": {
        "RateBasedStatement": {
          "Limit": 2000,
          "AggregateKeyType": "IP"
        }
      },
      "Action": {
        "Block": {}
      },
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "RateLimitRule"
      }
    }
  ]'
```

### Security Groups

```bash
# Create security group for application
aws ec2 create-security-group \
  --group-name ai-connect-app-sg \
  --description "Security group for AI Connect application servers"

# Allow HTTP/HTTPS from load balancer only
aws ec2 authorize-security-group-ingress \
  --group-name ai-connect-app-sg \
  --protocol tcp \
  --port 3000 \
  --source-group ai-connect-alb-sg
```

## Backup and Recovery

### Database Backup (if using RDS)

```bash
# Create RDS snapshot
aws rds create-db-snapshot \
  --db-instance-identifier ai-connect-db \
  --db-snapshot-identifier ai-connect-snapshot-$(date +%Y%m%d)

# Automate backups with Lambda function
```

### Application Backup

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="ai-connect-backup-$DATE"

# Create EBS snapshot
aws ec2 create-snapshot \
  --volume-id vol-1234567890abcdef0 \
  --description "$BACKUP_NAME"

# Backup configuration to S3
aws s3 cp /app/.env s3://ai-connect-backups/config/env-$DATE
EOF
```

## Cost Optimization

### Reserved Instances

```bash
# Purchase Reserved Instances for predictable workloads
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id 5ef06327-2e47-4e93-9dfa-7ff0e1f4c7dd \
  --instance-count 1
```

### Auto Scaling Configuration

```bash
# Create Auto Scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name ai-connect-asg \
  --launch-configuration-name ai-connect-lc \
  --min-size 1 \
  --max-size 5 \
  --desired-capacity 2 \
  --target-group-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/ai-connect-tg/50dc6c495c0c9188 \
  --health-check-type ELB \
  --health-check-grace-period 300

# Create scaling policies
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name ai-connect-asg \
  --policy-name ai-connect-scale-up \
  --scaling-adjustment 1 \
  --adjustment-type ChangeInCapacity
```

## Troubleshooting

### Common Issues

#### 1. Application Not Starting

```bash
# Check ECS task logs
aws logs get-log-events \
  --log-group-name /ecs/ai-connect \
  --log-stream-name ecs/ai-connect-container/task-id

# Check Elastic Beanstalk logs
eb logs
```

#### 2. SSL Certificate Issues

```bash
# Check certificate status
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012
```

#### 3. Load Balancer Health Checks Failing

```bash
# Check target group health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/ai-connect-tg/50dc6c495c0c9188
```

### Performance Optimization

1. **Use CloudFront for static assets**
2. **Implement Redis for session management**
3. **Use RDS Read Replicas for database scaling**
4. **Enable gzip compression**
5. **Optimize Docker images**

### Monitoring Commands

```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=ai-connect-service \
  --start-time 2025-10-21T00:00:00Z \
  --end-time 2025-10-21T23:59:59Z \
  --period 3600 \
  --statistics Average

# Check application logs
aws logs filter-log-events \
  --log-group-name /aws/ai-connect/application \
  --start-time 1697884800000 \
  --filter-pattern "ERROR"
```

## Next Steps

After deployment:

1. Set up CI/CD pipeline with AWS CodePipeline
2. Implement blue-green deployments
3. Configure automated testing
4. Set up comprehensive monitoring
5. Implement log aggregation with ELK stack
6. Configure disaster recovery procedures

For ongoing maintenance, refer to AWS best practices and regularly review AWS Well-Architected Framework guidelines.