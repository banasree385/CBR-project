# Azure Deployment Guide for AI Connect Website

This guide provides step-by-step instructions for deploying the AI Connect website to Microsoft Azure.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Azure Services Overview](#azure-services-overview)
3. [Deployment Methods](#deployment-methods)
4. [Method 1: Azure App Service](#method-1-azure-app-service)
5. [Method 2: Azure Container Instances](#method-2-azure-container-instances)
6. [Method 3: Azure Static Web Apps + Functions](#method-3-azure-static-web-apps--functions)
7. [Environment Configuration](#environment-configuration)
8. [Domain and SSL Setup](#domain-and-ssl-setup)
9. [Monitoring and Scaling](#monitoring-and-scaling)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

- Azure account with active subscription
- Azure CLI installed and configured
- Node.js 16+ installed locally
- Git repository with the AI Connect project

### Install Azure CLI

```bash
# Windows (using Chocolatey)
choco install azure-cli

# macOS (using Homebrew)
brew install azure-cli

# Login to Azure
az login
```

## Azure Services Overview

The AI Connect website can be deployed using several Azure services:

- **Azure App Service**: Best for Node.js applications with minimal configuration
- **Azure Container Instances**: For containerized deployments
- **Azure Static Web Apps**: For static frontend with serverless backend
- **Azure Virtual Machines**: For full control (not covered in this guide)

## Deployment Methods

## Method 1: Azure App Service

### Step 1: Create Resource Group

```bash
# Create a resource group
az group create \
  --name ai-connect-rg \
  --location "East US"
```

### Step 2: Create App Service Plan

```bash
# Create an App Service plan
az appservice plan create \
  --name ai-connect-plan \
  --resource-group ai-connect-rg \
  --sku B1 \
  --is-linux
```

### Step 3: Create Web App

```bash
# Create the web app
az webapp create \
  --resource-group ai-connect-rg \
  --plan ai-connect-plan \
  --name ai-connect-webapp \
  --runtime "NODE|18-lts" \
  --deployment-local-git
```

### Step 4: Configure Environment Variables

```bash
# Set environment variables
az webapp config appsettings set \
  --resource-group ai-connect-rg \
  --name ai-connect-webapp \
  --settings \
    NODE_ENV=production \
    PORT=8000 \
    OPENAI_API_KEY="your-openai-api-key" \
    EMAIL_SERVICE="gmail" \
    EMAIL_USER="your-email@gmail.com" \
    EMAIL_PASS="your-app-password" \
    CORS_ORIGIN="https://ai-connect-webapp.azurewebsites.net"
```

### Step 5: Deploy Code

```bash
# Add Azure remote
az webapp deployment source config-local-git \
  --name ai-connect-webapp \
  --resource-group ai-connect-rg

# Get deployment credentials
az webapp deployment list-publishing-credentials \
  --name ai-connect-webapp \
  --resource-group ai-connect-rg

# Deploy code
git remote add azure <git-clone-url-from-previous-command>
git push azure main
```

### Step 6: Configure Startup Command

```bash
# Set startup command
az webapp config set \
  --resource-group ai-connect-rg \
  --name ai-connect-webapp \
  --startup-file "backend/server.js"
```

## Method 2: Azure Container Instances

### Step 1: Create Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application
CMD ["node", "backend/server.js"]
```

### Step 2: Create and Push Container Image

```bash
# Create Azure Container Registry
az acr create \
  --resource-group ai-connect-rg \
  --name aiconnectacr \
  --sku Basic \
  --admin-enabled true

# Build and push image
az acr build \
  --registry aiconnectacr \
  --image ai-connect:latest .
```

### Step 3: Deploy Container Instance

```bash
# Get ACR credentials
ACR_SERVER=$(az acr show --name aiconnectacr --resource-group ai-connect-rg --query "loginServer" --output tsv)
ACR_USERNAME=$(az acr credential show --name aiconnectacr --resource-group ai-connect-rg --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name aiconnectacr --resource-group ai-connect-rg --query "passwords[0].value" --output tsv)

# Deploy container
az container create \
  --resource-group ai-connect-rg \
  --name ai-connect-container \
  --image $ACR_SERVER/ai-connect:latest \
  --registry-login-server $ACR_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --dns-name-label ai-connect-app \
  --ports 3000 \
  --environment-variables \
    NODE_ENV=production \
    OPENAI_API_KEY="your-openai-api-key" \
    EMAIL_SERVICE="gmail" \
    EMAIL_USER="your-email@gmail.com" \
    EMAIL_PASS="your-app-password"
```

## Method 3: Azure Static Web Apps + Functions

### Step 1: Prepare Static Assets

Create a build script to prepare static files:

```bash
# Create build directory structure
mkdir -p build/frontend
mkdir -p build/api

# Copy frontend files
cp -r frontend/* build/frontend/

# Create Azure Functions structure for API
# (This requires restructuring the backend as Azure Functions)
```

### Step 2: Create Static Web App

```bash
# Create Static Web App
az staticwebapp create \
  --name ai-connect-static \
  --resource-group ai-connect-rg \
  --source https://github.com/your-username/ai-connect-website \
  --location "East US 2" \
  --branch main \
  --app-location "build/frontend" \
  --api-location "build/api"
```

## Environment Configuration

### Required Environment Variables

```bash
# Production environment variables
NODE_ENV=production
PORT=8000

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Email Configuration
EMAIL_SERVICE=gmail
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# CORS Configuration
CORS_ORIGIN=https://your-domain.com

# Optional: Database Configuration (if added later)
# DATABASE_URL=your-database-connection-string
```

### Setting Environment Variables via Azure Portal

1. Navigate to your App Service in the Azure Portal
2. Go to **Configuration** > **Application settings**
3. Click **+ New application setting**
4. Add each environment variable
5. Click **Save**

### Setting Environment Variables via Azure CLI

```bash
# Set multiple environment variables
az webapp config appsettings set \
  --resource-group ai-connect-rg \
  --name ai-connect-webapp \
  --settings @env-settings.json
```

Create `env-settings.json`:

```json
[
  {
    "name": "NODE_ENV",
    "value": "production"
  },
  {
    "name": "OPENAI_API_KEY",
    "value": "your-openai-api-key"
  },
  {
    "name": "EMAIL_SERVICE",
    "value": "gmail"
  },
  {
    "name": "EMAIL_USER",
    "value": "your-email@gmail.com"
  },
  {
    "name": "EMAIL_PASS",
    "value": "your-app-password"
  }
]
```

## Domain and SSL Setup

### Step 1: Add Custom Domain

```bash
# Add custom domain
az webapp config hostname add \
  --webapp-name ai-connect-webapp \
  --resource-group ai-connect-rg \
  --hostname www.your-domain.com
```

### Step 2: Configure SSL Certificate

#### Option A: Managed Certificate (Recommended)

```bash
# Create managed certificate
az webapp config ssl create \
  --resource-group ai-connect-rg \
  --name ai-connect-webapp \
  --hostname www.your-domain.com
```

#### Option B: Upload Custom Certificate

```bash
# Upload certificate
az webapp config ssl upload \
  --certificate-file path/to/certificate.pfx \
  --certificate-password your-password \
  --name ai-connect-webapp \
  --resource-group ai-connect-rg

# Bind certificate
az webapp config ssl bind \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI \
  --name ai-connect-webapp \
  --resource-group ai-connect-rg
```

### Step 3: Configure DNS

Add the following DNS records to your domain provider:

```
Type: CNAME
Name: www
Value: ai-connect-webapp.azurewebsites.net

Type: A (if using apex domain)
Name: @
Value: [IP address from Azure Portal]
```

## Monitoring and Scaling

### Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app ai-connect-insights \
  --location "East US" \
  --resource-group ai-connect-rg \
  --application-type web

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app ai-connect-insights \
  --resource-group ai-connect-rg \
  --query "instrumentationKey" \
  --output tsv)

# Configure App Service to use Application Insights
az webapp config appsettings set \
  --resource-group ai-connect-rg \
  --name ai-connect-webapp \
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY"
```

### Configure Auto-scaling

```bash
# Create autoscale setting
az monitor autoscale create \
  --resource-group ai-connect-rg \
  --resource ai-connect-webapp \
  --resource-type Microsoft.Web/serverfarms \
  --name ai-connect-autoscale \
  --min-count 1 \
  --max-count 5 \
  --count 1

# Add scale-out rule
az monitor autoscale rule create \
  --resource-group ai-connect-rg \
  --autoscale-name ai-connect-autoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1

# Add scale-in rule
az monitor autoscale rule create \
  --resource-group ai-connect-rg \
  --autoscale-name ai-connect-autoscale \
  --condition "Percentage CPU < 30 avg 5m" \
  --scale in 1
```

### Set up Alerts

```bash
# Create action group for notifications
az monitor action-group create \
  --resource-group ai-connect-rg \
  --name ai-connect-alerts \
  --short-name aiconnect \
  --email admin your-email@domain.com

# Create CPU alert
az monitor metrics alert create \
  --name "High CPU Usage" \
  --resource-group ai-connect-rg \
  --scopes /subscriptions/{subscription}/resourceGroups/ai-connect-rg/providers/Microsoft.Web/sites/ai-connect-webapp \
  --condition "avg Percentage CPU > 80" \
  --action ai-connect-alerts \
  --description "Alert when CPU usage is high"
```

## Backup and Recovery

### Enable Backup

```bash
# Create storage account for backups
az storage account create \
  --name aiconnectbackups \
  --resource-group ai-connect-rg \
  --location "East US" \
  --sku Standard_LRS

# Configure backup
az webapp config backup update \
  --resource-group ai-connect-rg \
  --webapp-name ai-connect-webapp \
  --container-url "https://aiconnectbackups.blob.core.windows.net/backups" \
  --frequency 1 \
  --frequency-unit Day \
  --retain-one true \
  --retention-period-in-days 30
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Not Starting

```bash
# Check application logs
az webapp log tail \
  --name ai-connect-webapp \
  --resource-group ai-connect-rg

# Check configuration
az webapp config show \
  --name ai-connect-webapp \
  --resource-group ai-connect-rg
```

#### 2. Environment Variables Not Loading

```bash
# Verify environment variables
az webapp config appsettings list \
  --name ai-connect-webapp \
  --resource-group ai-connect-rg
```

#### 3. SSL Certificate Issues

```bash
# Check SSL configuration
az webapp config ssl list \
  --resource-group ai-connect-rg
```

#### 4. Performance Issues

- Enable Application Insights for detailed performance metrics
- Check resource utilization in Azure Portal
- Consider upgrading App Service plan
- Implement caching strategies

### Health Check Endpoint

The application includes a health check endpoint at `/api/health`. Monitor this endpoint to ensure your application is running correctly:

```bash
# Test health endpoint
curl https://your-app.azurewebsites.net/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T10:00:00.000Z",
  "version": "1.0.0",
  "environment": "production"
}
```

## Security Best Practices

1. **Enable HTTPS Only**:
   ```bash
   az webapp update \
     --resource-group ai-connect-rg \
     --name ai-connect-webapp \
     --https-only true
   ```

2. **Configure IP Restrictions** (if needed):
   ```bash
   az webapp config access-restriction add \
     --resource-group ai-connect-rg \
     --name ai-connect-webapp \
     --rule-name "Allow Office IP" \
     --action Allow \
     --ip-address 203.0.113.0/24 \
     --priority 100
   ```

3. **Enable Managed Identity** (for secure Azure service access):
   ```bash
   az webapp identity assign \
     --name ai-connect-webapp \
     --resource-group ai-connect-rg
   ```

## Cost Optimization

1. **Use appropriate App Service plan size**
2. **Enable auto-scaling to handle traffic spikes**
3. **Monitor usage with Azure Cost Management**
4. **Consider Azure CDN for static assets**
5. **Use Azure Monitor to track performance metrics**

## Next Steps

After successful deployment:

1. Set up continuous deployment with GitHub Actions
2. Configure monitoring and alerting
3. Set up staging environment
4. Implement automated testing
5. Configure backup strategies
6. Set up log aggregation and analysis

For ongoing maintenance and updates, refer to the Azure App Service documentation and best practices.