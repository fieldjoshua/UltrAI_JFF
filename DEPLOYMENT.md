# UltrAI Deployment Guide

## Render Deployment

UltrAI is configured for one-click deployment to Render using the included `render.yaml` configuration.

### Prerequisites

1. **Render Account**: Sign up at https://render.com
2. **OpenRouter API Key**: Get your key from https://openrouter.ai/keys
3. **GitHub Repository**: Connect your GitHub account to Render

### Deployment Steps

#### Option 1: Deploy from GitHub (Recommended)

1. **Connect Repository to Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Select "Connect a repository"
   - Choose the UltrAI_JFF repository
   - Render will automatically detect `render.yaml`

2. **Configure Environment Variables**
   - Render will prompt you to set `OPENROUTER_API_KEY`
   - Enter your OpenRouter API key
   - Other environment variables are pre-configured in `render.yaml`

3. **Deploy**
   - Click "Apply" to start deployment
   - Render will:
     - Install Python 3.11
     - Install dependencies from `requirements.txt`
     - Start the FastAPI server with uvicorn
     - Run health checks on `/health` endpoint

4. **Access Your API**
   - Your API will be available at: `https://ultrai-api.onrender.com`
   - Health check: `https://ultrai-api.onrender.com/health`

#### Option 2: Manual Web Service Creation

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Name**: `ultrai-api`
   - **Region**: Oregon (or your preferred region)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -U pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn ultrai.api:app --host 0.0.0.0 --port $PORT --workers 3`
   - **Plan**: Starter (or higher)
5. Add Environment Variables:
   - `OPENROUTER_API_KEY` (your API key)
   - `YOUR_SITE_URL` (your Render URL)
   - `YOUR_SITE_NAME` (e.g., "UltrAI Synthesis API")
6. Deploy

### API Endpoints

Once deployed, your API will expose:

- **POST /runs** - Start new synthesis run
  ```bash
  curl -X POST https://ultrai-api.onrender.com/runs \
    -H "Content-Type: application/json" \
    -d '{"query": "What is quantum computing?", "cocktail": "SPEEDY"}'
  ```
  Response: `{"run_id": "api_speedy_20251017_120000"}`

- **GET /runs/{run_id}/status** - Check run status
  ```bash
  curl https://ultrai-api.onrender.com/runs/api_speedy_20251017_120000/status
  ```

- **GET /runs/{run_id}/artifacts** - List run artifacts
  ```bash
  curl https://ultrai-api.onrender.com/runs/api_speedy_20251017_120000/artifacts
  ```

- **GET /health** - Health check
  ```bash
  curl https://ultrai-api.onrender.com/health
  ```
  Response: `{"status": "ok"}`

### Configuration Files

- **render.yaml** - Blueprint configuration for Render deployment
- **runtime.txt** - Python version specification (3.11.0)
- **requirements.txt** - Python dependencies
- **.env** (local only) - Environment variables for local development

### Production Configuration

The `render.yaml` includes production-ready settings:

- **Workers**: 3 uvicorn workers for concurrent request handling
- **Region**: Oregon (lowest latency for US users)
- **Health Checks**: Automatic monitoring via `/health` endpoint
- **Plan**: Starter (can be upgraded to Standard/Pro for more resources)

### Environment Variables

Required:
- `OPENROUTER_API_KEY` - Your OpenRouter API key (set in Render dashboard)

Optional (pre-configured):
- `YOUR_SITE_URL` - Your site URL for OpenRouter identification
- `YOUR_SITE_NAME` - Your site name for OpenRouter identification
- `PYTHON_VERSION` - Python version (3.11.0)

### Monitoring and Logs

1. **Render Dashboard**: https://dashboard.render.com
   - View deployment status
   - Monitor resource usage
   - Access real-time logs

2. **Health Checks**: Automatic monitoring via `/health` endpoint
   - Render pings `/health` every few minutes
   - Service auto-restarts on health check failures

3. **Logs**: Available in Render dashboard
   - Application logs
   - Build logs
   - Error tracking

### Storage and Artifacts

**Important**: Render's free/starter plans use ephemeral storage. Run artifacts (`runs/<run_id>/`) are:
- Created during execution
- Available during the service lifetime
- **Lost on service restart or re-deployment**

For persistent storage, consider:
1. Upgrading to a plan with persistent disk
2. Using external storage (S3, Cloud Storage)
3. Downloading artifacts via API before restart

### Scaling

Render supports automatic scaling:

1. **Horizontal Scaling**: Add more instances (Standard/Pro plans)
2. **Vertical Scaling**: Upgrade to higher-tier plans for more CPU/RAM
3. **Workers**: Increase `--workers` in `startCommand` (limited by plan CPU)

### Security

The API includes security measures:
- Path traversal protection via `_sanitize_run_id()` and `_build_runs_dir()`
- Input validation on all endpoints
- HTTPS by default (Render provides SSL certificates)
- Environment variable encryption (Render encrypts `OPENROUTER_API_KEY`)

### Troubleshooting

**Build Failures:**
- Check Python version in `runtime.txt` matches `requirements.txt`
- Verify all dependencies are in `requirements.txt`
- Review build logs in Render dashboard

**Health Check Failures:**
- Ensure `/health` endpoint returns 200 OK
- Check if `OPENROUTER_API_KEY` is set (system readiness may fail without it)
- Review application logs for errors

**Slow Responses:**
- Upgrade to Standard/Pro plan for more resources
- Increase workers in `startCommand`
- Consider caching or CDN for static content

**Missing Artifacts:**
- Remember: ephemeral storage is cleared on restart
- Download artifacts before redeployment
- Consider persistent disk or external storage

### Local Development

Run the API locally:

```bash
# Activate virtual environment
. .venv/bin/activate

# Set environment variable
export OPENROUTER_API_KEY=your_key_here

# Start server
uvicorn ultrai.api:app --reload --host 0.0.0.0 --port 8000

# Access at http://localhost:8000
```

### Continuous Deployment

Render supports automatic deployments:

1. **Auto-Deploy**: Enabled by default for the `main` branch
2. **Manual Deploy**: Trigger from Render dashboard
3. **PR Previews**: Available on Pro plans (optional)

Every push to `main` automatically triggers:
1. Build process (install dependencies)
2. Deploy new version
3. Health check verification
4. Traffic cutover (zero-downtime)

### Cost Estimation

**Starter Plan** (recommended for testing/development):
- $7/month
- 512 MB RAM
- 0.5 CPU
- Automatic HTTPS
- Suitable for light usage

**Standard Plan** (recommended for production):
- $25/month
- 2 GB RAM
- 1 CPU
- Horizontal scaling
- Persistent disk available

**Pro Plans**: $85-$460/month for higher resource needs

### Support

- **Render Documentation**: https://render.com/docs
- **Render Community**: https://community.render.com
- **GitHub Issues**: Report bugs at https://github.com/fieldjoshua/UltrAI_JFF/issues
