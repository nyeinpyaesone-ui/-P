# Render Integration Setup Guide

## Prerequisites

1. **Render Account**: Sign up at [https://render.com](https://render.com)
2. **GitHub Repository**: This repository connected to GitHub Actions

## Configuration Steps

### 1. Create a Service on Render

1. Log in to your [Render Dashboard](https://dashboard.render.com)
2. Click **New +** and select your service type:
   - **Web Service**: For web applications and APIs
   - **Static Site**: For static websites
   - **Background Worker**: For background jobs
   - **PostgreSQL/Redis**: For databases

3. Connect your GitHub repository
4. Configure your service settings:
   - **Name**: Your service name
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: Leave blank if code is in root
   - **Runtime**: Select appropriate runtime (Node, Python, Docker, etc.)
   - **Build Command**: e.g., `npm install` or `pip install -r requirements.txt`
   - **Start Command**: e.g., `npm start` or `python app.py`

### 2. Get Render Credentials

#### API Key
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click your profile icon → **API Keys**
3. Click **Create API Key**
4. Copy the generated key (store it securely)

#### Service ID
1. Navigate to your service in the Render Dashboard
2. The Service ID is in the URL: `https://dashboard.render.com/detail/{SERVICE_ID}`
3. Or find it in the service settings under **Settings** → **Service ID**

### 3. Add Secrets to GitHub

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `RENDER_API_KEY` | Your Render API key | Authentication for Render API |
| `RENDER_SERVICE_ID` | Your service ID from Render | Identifies which service to deploy |

### 4. Deploy

The workflow will automatically deploy when you:
- Push to the `main` branch
- Manually trigger the workflow from the Actions tab

## Manual Deployment

1. Go to **Actions** tab in your GitHub repository
2. Select **Deploy to Render** workflow
3. Click **Run workflow**
4. Select environment (production/preview)
5. (Optional) Add custom environment variables in JSON format:
   ```json
   {"NODE_ENV": "production", "API_URL": "https://api.example.com"}
   ```
6. Click **Run workflow**

## Environment Variables

### Global Workflow Variables
These are set in the workflow file and apply to all deployments:
- `NODE_ENV`: Set to `production`
- `RENDER_REGION`: Set to `us-east`

### Custom Runtime Variables
You can pass custom environment variables during manual deployment:

1. When triggering the workflow manually, use the **Environment Variables** input field
2. Provide variables in JSON format:
   ```json
   {"KEY1": "value1", "KEY2": "value2"}
   ```
3. These variables will be available during the deployment process

### Render Service Variables
To add persistent environment variables to your Render service:

1. Go to Render Dashboard → Your Service → **Environment**
2. Add key-value pairs
3. These will be available during build and runtime on Render

## Troubleshooting

### Deployment Fails
- Check GitHub Actions logs for error messages
- Verify API key and Service ID are correct
- Ensure Render service is properly configured
- Check Render dashboard for deployment logs

### Permission Issues
- Ensure API key has proper permissions
- Verify GitHub Actions has write access to the repository

### Build Failures
- Review build command configuration in Render
- Check that all dependencies are properly specified
- Verify start command matches your application

## Environment Variables

To add environment variables to your Render service:

1. Go to Render Dashboard → Your Service → **Environment**
2. Add key-value pairs
3. These will be available during build and runtime

## Auto-Deploy Settings

In Render Dashboard, you can configure:
- **Auto-Deploy**: Enable/disable automatic deployments on push
- **Preview Environments**: Automatic preview deployments for pull requests

## Useful Links

- [Render Documentation](https://render.com/docs)
- [Render API Reference](https://api-docs.render.com)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Render GitHub Action](https://github.com/render-oss/github-action)
