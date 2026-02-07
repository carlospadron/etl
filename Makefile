.PHONY: help setup-local start-local stop-local clean-local seed-data terraform-init terraform-plan terraform-apply terraform-destroy

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[1;33m
NC     := \033[0m

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${GREEN}%-20s${NC} %s\n", $$1, $$2}' $(MAKEFILE_LIST)

##@ Local Development (Docker Compose)

setup-local: ## Complete setup: start databases and seed data
	@echo "${GREEN}Setting up local environment...${NC}"
	@bash setup-local.sh

start-local: ## Start local PostgreSQL databases with Docker Compose
	@echo "${GREEN}Starting local databases...${NC}"
	@if command -v docker-compose > /dev/null 2>&1; then \
		docker-compose up -d; \
	else \
		docker compose up -d; \
	fi
	@echo "${GREEN}Databases started. Source on port 5432, Target on port 5433${NC}"

stop-local: ## Stop local databases
	@echo "${YELLOW}Stopping local databases...${NC}"
	@if command -v docker-compose > /dev/null 2>&1; then \
		docker-compose stop; \
	else \
		docker compose stop; \
	fi

clean-local: ## Stop and remove local databases and volumes
	@echo "${YELLOW}Cleaning up local databases...${NC}"
	@if command -v docker-compose > /dev/null 2>&1; then \
		docker-compose down -v; \
	else \
		docker compose down -v; \
	fi
	@echo "${GREEN}Cleanup complete${NC}"

logs-local: ## Show logs from local databases
	@if command -v docker-compose > /dev/null 2>&1; then \
		docker-compose logs -f; \
	else \
		docker compose logs -f; \
	fi

seed-data: ## Seed data into local source database (requires CSV file in data/)
	@echo "${GREEN}Seeding data...${NC}"
	@if [ ! -f "data/osopenuprn_202502.csv" ]; then \
		echo "${YELLOW}Warning: CSV file not found at data/osopenuprn_202502.csv${NC}"; \
		echo "Download from: https://osdatahub.os.uk/downloads/open/OpenUPRN"; \
		exit 1; \
	fi
	@cd data && bash initial_upload.sh

##@ AWS Deployment (Terraform)

terraform-init: ## Initialize Terraform
	@echo "${GREEN}Initializing Terraform...${NC}"
	@cd terraform && terraform init

terraform-validate: ## Validate Terraform configuration
	@echo "${GREEN}Validating Terraform configuration...${NC}"
	@cd terraform && terraform validate

terraform-plan: ## Show Terraform execution plan
	@echo "${GREEN}Creating Terraform plan...${NC}"
	@cd terraform && terraform plan

terraform-apply: ## Apply Terraform configuration to create AWS infrastructure
	@echo "${GREEN}Applying Terraform configuration...${NC}"
	@cd terraform && terraform apply

terraform-destroy: ## Destroy AWS infrastructure created by Terraform
	@echo "${YELLOW}Destroying Terraform infrastructure...${NC}"
	@cd terraform && terraform destroy

terraform-output: ## Show Terraform outputs
	@cd terraform && terraform output

##@ Testing

test-pg-dump: ## Test pg_dump/restore ETL method
	@echo "${GREEN}Testing pg_dump/restore...${NC}"
	@docker build -t etl-pg-dump ./pg_dump_restore
	@docker run --rm --network host \
		-e ORIGIN_ADDRESS=localhost \
		-e ORIGIN_DB=postgres \
		-e ORIGIN_USER=postgres \
		-e ORIGIN_PASS=postgres \
		-e TARGET_ADDRESS=localhost \
		-e TARGET_DB=target \
		-e TARGET_USER=postgres \
		-e TARGET_PASS=postgres \
		etl-pg-dump

##@ Utility

check-deps: ## Check if required dependencies are installed
	@echo "${GREEN}Checking dependencies...${NC}"
	@command -v docker >/dev/null 2>&1 || { echo "docker is required but not installed."; exit 1; }
	@command -v psql >/dev/null 2>&1 || { echo "postgresql-client is required but not installed."; exit 1; }
	@if command -v docker-compose > /dev/null 2>&1 || docker compose version > /dev/null 2>&1; then \
		echo "docker-compose: OK"; \
	else \
		echo "docker-compose is required but not installed."; \
		exit 1; \
	fi
	@echo "${GREEN}All dependencies are installed${NC}"

.DEFAULT_GOAL := help
