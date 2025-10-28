.PHONY: help build run dev prod stop clean logs test shell

# Default target
.DEFAULT_GOAL := help

# Variables
DOCKER_IMAGE = ai-quote-generator
CONTAINER_NAME = ai-quote-generator
COMPOSE_DEV = docker-compose
COMPOSE_PROD = docker-compose -f docker-compose.prod.yml

help: ## Show this help message
	@echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
	@echo 'AI Quote Generator - Docker Commands'
	@echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
	@echo ''
	@echo 'Usage: make <target>'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''

build: ## Build the Docker image
	@echo "🔨 Building Docker image..."
	docker build -t $(DOCKER_IMAGE) .
	@echo "Image built successfully!"

run: build ## Build and run the container
	@echo "Starting container..."
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p 8000:8000 \
		--env-file .env \
		$(DOCKER_IMAGE)
	@echo "Container is running!"
	@echo "Access at: http://localhost:8000"

dev: ## Start in development mode (hot reload)
	@echo "Starting in development mode..."
	$(COMPOSE_DEV) up -d --build
	@echo "Development environment is running!"
	@echo "Access at: http://localhost:8000"
	@echo "View logs: make logs"

prod: ## Start in production mode
	@echo "Starting in production mode..."
	$(COMPOSE_PROD) up -d --build
	@echo "Production environment is running!"
	@echo "Access at: http://localhost:8000"

stop: ## Stop all running containers
	@echo "Stopping containers..."
	-$(COMPOSE_DEV) down 2>/dev/null || true
	-$(COMPOSE_PROD) down 2>/dev/null || true
	-docker stop $(CONTAINER_NAME) 2>/dev/null || true
	-docker rm $(CONTAINER_NAME) 2>/dev/null || true
	@echo "All containers stopped"

clean: stop ## Stop containers and remove images
	@echo "Cleaning up..."
	-docker rmi $(DOCKER_IMAGE) 2>/dev/null || true
	-docker system prune -f
	@echo "Cleanup complete"

logs: ## Show container logs (development)
	@echo "Showing logs (Ctrl+C to exit)..."
	$(COMPOSE_DEV) logs -f

logs-prod: ## Show container logs (production)
	@echo "Showing production logs (Ctrl+C to exit)..."
	$(COMPOSE_PROD) logs -f

test: ## Run tests inside container
	@echo "Running tests..."
	docker run --rm \
		--env-file .env \
		$(DOCKER_IMAGE) \
		pytest tests/ -v

shell: ## Open a shell in the container
	@echo "Opening shell in container..."
	docker exec -it $(CONTAINER_NAME) /bin/bash

shell-compose: ## Open a shell in the docker-compose container
	@echo "Opening shell in docker-compose container..."
	$(COMPOSE_DEV) exec web /bin/bash

restart: ## Restart containers
	@echo "Restarting containers..."
	$(COMPOSE_DEV) restart
	@echo "Containers restarted"

ps: ## Show running containers
	@echo "Running containers:"
	@docker ps --filter "name=$(CONTAINER_NAME)"

stats: ## Show container resource usage
	@echo "Container stats (Ctrl+C to exit):"
	docker stats $(CONTAINER_NAME)

health: ## Check application health
	@echo "Checking application health..."
	@curl -f http://localhost:8000/health || echo "Health check failed"

deploy: ## Run the deployment script
	@./deploy.sh

# Quick start commands
quick-dev: ## Quick start for development (same as dev)
	@$(MAKE) dev

quick-prod: ## Quick start for production (same as prod)
	@$(MAKE) prod

# Update and rebuild
rebuild: clean build ## Clean and rebuild everything
	@echo "Rebuild complete"

rebuild-dev: stop dev ## Rebuild and start in dev mode
	@echo "Development rebuild complete"

rebuild-prod: stop prod ## Rebuild and start in prod mode
	@echo "Production rebuild complete"
