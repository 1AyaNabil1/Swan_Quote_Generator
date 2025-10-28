# 🐳 Docker Quick Reference

## Quick Start Commands

### Using the Deployment Script (Easiest)
```bash
./deploy.sh
```

### Using Makefile (Recommended)
```bash
# Show all available commands
make help

# Development mode with hot reload
make dev

# Production mode
make prod

# View logs
make logs

# Stop all containers
make stop

# Clean up everything
make clean
```

### Using Docker Compose
```bash
# Development
docker-compose up -d
docker-compose logs -f
docker-compose down

# Production
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml down
```

### Using Docker Directly
```bash
# Build
docker build -t ai-quote-generator .

# Run
docker run -d -p 8000:8000 --env-file .env --name ai-quote-generator ai-quote-generator

# Logs
docker logs -f ai-quote-generator

# Stop
docker stop ai-quote-generator
docker rm ai-quote-generator
```

## Access Points

- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Troubleshooting

### Container won't start
```bash
docker logs ai-quote-generator
```

### Check if container is running
```bash
docker ps
```

### Check resource usage
```bash
docker stats ai-quote-generator
```

### Access container shell
```bash
docker exec -it ai-quote-generator /bin/bash
```

## Environment Variables

Required in `.env` file:
- `GEMINI_API_KEY` - Your Google Gemini API key

Optional:
- `DEBUG=False` - Set to False for production
- `PORT=8000` - Application port
- `DEFAULT_MODEL=gemini-1.5-flash` - AI model to use

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.
