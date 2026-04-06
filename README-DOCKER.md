# Docker Quick Start Guide

Run RAGY with a single command using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Tavily API key ([get free key](https://tavily.com/))

## Quick Start

### 1. Clone and Configure

```bash
# Clone repository
git clone https://github.com/Arseni1919/ragy.git
cd ragy

# Copy environment template
cp .env.example .env

# Edit .env and add your Tavily API key
nano .env  # or use your preferred editor
```

### 2. Start RAGY

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Check health
curl http://localhost:8000/api/v1/system/health
```

That's it! The API is now running at http://localhost:8000

### 3. Access the System

**Swagger UI (Interactive API docs):**
```
http://localhost:8000/docs
```

**CLI (via Docker exec):**
```bash
# Access CLI inside container
docker-compose exec ragy-api /app/.venv/bin/python -m ragy_cli.cli

# Or with bash alias
docker-compose exec ragy-api bash
# Inside container: python -m ragy_cli.cli
```

**API Endpoints:**
```bash
# List collections
curl http://localhost:8000/api/v1/extract/collections

# Health check
curl http://localhost:8000/api/v1/system/health

# Create index (example)
curl -X POST http://localhost:8000/api/v1/index/create \
  -H "Content-Type: application/json" \
  -d '{"query": "AI news", "collection_name": "ai_2024", "num_days": 7}'
```

## Management Commands

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v

# Restart
docker-compose restart

# View logs
docker-compose logs -f ragy-api

# Shell access
docker-compose exec ragy-api bash

# Rebuild after code changes
docker-compose up -d --build
```

## Data Persistence

Data is stored in Docker volumes and local directories:

- `./ragy_db/` - ChromaDB vector database
- `./ragy_jobs.db` - Scheduled jobs metadata
- `models_cache` volume - Cached Hugging Face models

These persist across container restarts. To delete all data:

```bash
docker-compose down -v
rm -rf ragy_db ragy_jobs.db
```

## First Run Notes

**Model Download:**
- On first query, embedding models (~80MB) download automatically
- This takes 10-60 seconds depending on internet speed
- Subsequent queries are instant (models cached)

**Resource Usage:**
- Memory: ~1-2GB (embedding models)
- Disk: ~500MB-2GB (model cache)
- CPU: Variable (depends on concurrent operations)

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs ragy-api

# Common issue: missing TAVILY_API_KEY
# Solution: Verify .env file has valid key
```

### Health check failing

```bash
# Check if API is running
docker-compose ps

# View detailed logs
docker-compose logs -f ragy-api

# Test health endpoint manually
curl -v http://localhost:8000/api/v1/system/health
```

### Out of memory

```bash
# Increase memory limit in docker-compose.yml
# Change: memory: 2G → memory: 4G
docker-compose up -d --build
```

### Models not downloading

```bash
# Check internet connectivity from container
docker-compose exec ragy-api curl -I https://huggingface.co

# Check disk space
docker-compose exec ragy-api df -h

# Clear model cache and retry
docker-compose down -v
docker volume rm ragy_models_cache
docker-compose up -d
```

## Development Mode

For development with hot reload:

```bash
# Add volume mount for code in docker-compose.override.yml
# (Not recommended for production)
```

## Production Deployment

For production:

1. Use specific version tags (not `latest`)
2. Set up proper secrets management (not .env files)
3. Configure reverse proxy (Nginx, Caddy)
4. Enable HTTPS
5. Set up monitoring and logging
6. Use Docker Swarm or Kubernetes for orchestration

## Advanced Configuration

### Custom Model

```bash
# In .env
HF_EMB_MODEL=google/embeddinggemma-300m

# Restart
docker-compose restart
```

### Disable Scheduler

```bash
# In .env
SCHEDULER_ENABLED=false

# Restart
docker-compose restart
```

### Change Port

```bash
# In docker-compose.yml, change ports mapping
ports:
  - "3000:8000"  # Host:Container

# Rebuild
docker-compose up -d
```

## FAQ

**Q: Do I need to install Python or uv?**
A: No! Docker handles everything.

**Q: Can I use the CLI?**
A: Yes, via `docker-compose exec ragy-api /app/.venv/bin/python -m ragy_cli.cli`

**Q: How do I update RAGY?**
A: `git pull && docker-compose up -d --build`

**Q: Is my data safe?**
A: Yes, data persists in volumes. Back up `ragy_db/` and `ragy_jobs.db` regularly.

**Q: Can I run multiple instances?**
A: Yes, change ports and volume names in docker-compose.yml

## Support

- **Issues**: https://github.com/Arseni1919/ragy/issues
- **Discussions**: https://github.com/Arseni1919/ragy/discussions
- **Documentation**: https://github.com/Arseni1919/ragy#readme
