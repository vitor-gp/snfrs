# SNFRS Deployment Guide

This guide covers deploying SNFRS in production and development environments using Docker.

## 🚀 Quick Deployment

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Environment variables** configured (see [Environment Setup](#environment-setup))

### Production Deployment

```bash
# Clone the repository
git clone <repository-url>
cd snfrs

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

## 🔧 Environment Setup

### Required Environment Variables

Create a `.env` file in the project root:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_ADMIN_ROLE=Admin
DISCORD_ADMIN_PASSWORD=your_admin_password

# API Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./data/app.db
API_BASE_URL=http://api:8000

# Optional: Database (for PostgreSQL)
# DATABASE_URL=postgresql://user:password@localhost/snfrs
```

### Discord Bot Setup

1. **Create Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application
   - Go to "Bot" section
   - Copy the bot token to `DISCORD_TOKEN`

2. **Bot Permissions**
   - Enable "applications.commands" scope
   - Add bot to your Discord server
   - Ensure bot has permission to send messages

3. **Admin Role Configuration**
   - Set `DISCORD_ADMIN_ROLE` to match your Discord server's admin role name
   - Set `DISCORD_ADMIN_PASSWORD` for the `/make_admin` command

## 🐳 Docker Deployment

### Docker Compose Services

The application consists of two main services:

```yaml
services:
  api:          # FastAPI backend
  discord-bot:  # Discord bot
```

### Production Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update and restart
git pull
docker-compose down
docker-compose up -d --build
```

### Development Deployment

```bash
# Start with development overrides
make docker-dev

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 📊 Monitoring and Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f discord-bot

# Recent logs only
docker-compose logs --tail=100 -f
```

### Health Checks

```bash
# API health check
curl http://localhost:8000/health

# Check service status
docker-compose ps
```

### Container Management

```bash
# Restart specific service
docker-compose restart discord-bot

# Rebuild and restart
docker-compose up -d --build discord-bot

# Scale services (if needed)
docker-compose up -d --scale api=2
```

## 🗄️ Database Management

### SQLite (Default)

```bash
# Database is stored in ./data/app.db
# Backup database
cp data/app.db data/app.db.backup

# Reset database
rm data/app.db
docker-compose restart api
```

### PostgreSQL (Production)

For production, consider using PostgreSQL:

```yaml
# docker-compose.prod.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: snfrs
      POSTGRES_USER: snfrs
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

Update `.env`:
```env
DATABASE_URL=postgresql://snfrs:your_password@db:5432/snfrs
```

### Database Migrations

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "Description"
```

## 🔒 Security Considerations

### Production Security

1. **Environment Variables**
   - Use strong, unique passwords
   - Generate secure `SECRET_KEY`
   - Keep Discord token secure

2. **Network Security**
   - Use reverse proxy (nginx/traefik)
   - Enable HTTPS/TLS
   - Restrict database access

3. **Container Security**
   - Run containers as non-root user
   - Use official base images
   - Keep images updated

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔄 Backup and Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
cp data/app.db "backups/app_${DATE}.db"

# Backup environment
cp .env "backups/env_${DATE}.backup"

# Keep only last 30 days
find backups/ -name "*.db" -mtime +30 -delete
```

### Recovery

```bash
# Stop services
docker-compose down

# Restore database
cp backups/app_20240620_120000.db data/app.db

# Restart services
docker-compose up -d
```

## 📈 Performance Optimization

### Resource Limits

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

### Scaling Considerations

1. **Database**: Use PostgreSQL for production
2. **Caching**: Add Redis for session/cache storage
3. **Load Balancing**: Use multiple API instances
4. **Monitoring**: Add Prometheus/Grafana

## 🚨 Troubleshooting

### Common Issues

1. **Discord Bot Not Connecting**
   ```bash
   # Check token and permissions
   docker-compose logs discord-bot
   ```

2. **Database Connection Issues**
   ```bash
   # Check database file permissions
   ls -la data/
   docker-compose restart api
   ```

3. **Port Conflicts**
   ```bash
   # Change ports in docker-compose.yml
   ports:
     - "8001:8000"  # Use different external port
   ```

4. **Memory Issues**
   ```bash
   # Check container resource usage
   docker stats
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose up

# Or edit docker-compose.yml
environment:
  - LOG_LEVEL=DEBUG
```

## 📞 Support

- **Logs**: Always include relevant logs when reporting issues
- **Environment**: Specify deployment environment (Docker, local, etc.)
- **Version**: Include Git commit hash or tag
- **Configuration**: Check environment variables and Docker setup 