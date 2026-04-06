# Railway Deployment Guide

Deploy RAGY as a hosted demo with one click.

## Prerequisites

- Railway account ([sign up free](https://railway.app/))
- GitHub account (for auto-deploy)
- Tavily API key ([get free key](https://tavily.com/))

## Deployment Steps

### 1. Fork Repository

Fork https://github.com/Arseni1919/ragy to your GitHub account.

### 2. Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your forked `ragy` repository
5. Railway will auto-detect the Dockerfile

### 3. Configure Environment Variables

In Railway project settings, add:

**Required:**
- `TAVILY_API_KEY` = your-tavily-key
- `DEMO_MODE` = true
- `PORT` = 8000 (Railway provides this automatically)

**Optional:**
- `HF_EMB_MODEL` = all-MiniLM-L6-v2
- `SCHEDULER_ENABLED` = false (disable for demo to save resources)
- `RAGY_MAX_CONCURRENT` = 2 (lower for free tier)

### 4. Add Volumes (Persistent Storage)

In Railway project settings:
1. Go to "Volumes"
2. Add volume: `/app/ragy_db` (ChromaDB data)
3. Add volume: `/app/ragy_jobs.db` (Jobs metadata)

### 5. Deploy

Railway will automatically deploy. Monitor logs for:
- Build progress
- Server startup
- Health checks passing

### 6. Seed Demo Collection

After first deployment:

```bash
# Using Railway CLI
railway run python demo_seed.py

# Or via Railway dashboard shell
# Navigate to project → Shell → run command
```

This creates `ai_news_demo` collection with 7 days of data.

### 7. Access Your Demo

Your demo will be available at:
```
https://your-project.railway.app/docs
```

**Demo Features:**
- ✅ Query existing collections
- ✅ Extract documents by similarity
- ✅ View database statistics
- ✅ Health checks
- ❌ Create new collections (read-only)
- ❌ Delete collections (read-only)
- ❌ Upload files (read-only)

## Auto-Deploy

Railway automatically deploys on git push:
1. Push changes to your fork
2. Railway detects commit
3. Rebuilds and redeploys
4. Zero downtime

## Monitoring

**Health Check:**
```bash
curl https://your-project.railway.app/api/v1/system/health
```

**Logs:**
- Railway Dashboard → Project → Logs

**Metrics:**
- Railway Dashboard → Project → Metrics
- Memory, CPU, requests/sec

## Cost Estimation

**Railway Free Tier:**
- $5/month credit
- ~500 hours runtime
- 512MB RAM
- 1GB storage

**Typical Usage:**
- Demo with 1 collection: ~200MB RAM
- 7-day index: ~50MB storage
- Should fit in free tier for demo purposes

**Upgrade if needed:**
- Pro plan: $20/month
- More resources for production use

## Troubleshooting

### Build fails

- Check Dockerfile syntax
- Verify all dependencies in pyproject.toml
- Check Railway build logs

### Out of memory

- Reduce `HF_EMB_MODEL` size
- Use smaller model (all-MiniLM-L6-v2)
- Upgrade Railway plan

### Demo not responding

- Check health endpoint
- View logs in Railway dashboard
- Verify environment variables set

## Security Best Practices

1. **Never commit .env files**
2. **Use Railway environment variables**
3. **Enable DEMO_MODE=true** (blocks writes)
4. **Disable scheduler** (SCHEDULER_ENABLED=false)
5. **Monitor usage** (watch for abuse)

## Production Deployment

For production (not demo):
- Use custom domain
- Enable HTTPS (Railway provides free SSL)
- Remove DEMO_MODE restriction
- Set up backups (volumes)
- Monitor costs and usage
- Consider using Railway's database add-ons

## Alternative Platforms

### Render

Similar to Railway:
1. Import from GitHub
2. Dockerfile detected automatically
3. Add environment variables
4. Deploy

### Fly.io

More powerful but complex:
```bash
fly launch
fly secrets set TAVILY_API_KEY=xxx
fly deploy
```

## Support

- **Railway Docs**: https://docs.railway.app/
- **RAGY Issues**: https://github.com/Arseni1919/ragy/issues
