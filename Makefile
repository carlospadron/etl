.PHONY: help setup-local start-local stop-local clean-local seed-data test-all test-etl build-all terraform-init terraform-plan terraform-apply terraform-destroy

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
	@if docker compose version > /dev/null 2>&1; then \
		docker compose up -d; \
	else \
		docker-compose up -d; \
	fi
	@echo "${GREEN}Databases started. Source on port 5432, Target on port 5433${NC}"

stop-local: ## Stop local databases
	@echo "${YELLOW}Stopping local databases...${NC}"
	@if docker compose version > /dev/null 2>&1; then \
		docker compose stop; \
	else \
		docker-compose stop; \
	fi

clean-local: ## Stop and remove local databases and volumes
	@echo "${YELLOW}Cleaning up local databases...${NC}"
	@if docker compose version > /dev/null 2>&1; then \
		docker compose down -v; \
	else \
		docker-compose down -v; \
	fi
	@echo "${GREEN}Cleanup complete${NC}"

logs-local: ## Show logs from local databases
	@if docker compose version > /dev/null 2>&1; then \
		docker compose logs -f; \
	else \
		docker-compose logs -f; \
	fi

seed-data: ## Seed data into local source database (requires CSV file in data/)
	@echo "${GREEN}Seeding data...${NC}"
	@CSV_FILE=$$(ls data/osopenuprn_*.csv 2>/dev/null | head -1); \
	if [ -z "$$CSV_FILE" ]; then \
		echo "${YELLOW}Warning: No CSV file found matching data/osopenuprn_*.csv${NC}"; \
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

test-all: ## Run all ETL benchmarks (builds, runs, monitors, validates, reports)
	@echo "${GREEN}Running all ETL benchmarks...${NC}"
	@bash run_tests.sh

test-etl: ## Run a specific ETL benchmark. Usage: make test-etl ETL=duckdb_copy
	@if [ -z "$(ETL)" ]; then \
		echo "${YELLOW}Usage: make test-etl ETL=<method_name>${NC}"; \
		echo "Available methods:"; \
		echo "  duckdb_copy duckdb_copy_parquet pandas_copy pandas_to_sql"; \
		echo "  pg_dump_restore polars_adbc_copy polars_connectorx_copy"; \
		echo "  polars_connectorx_write pyspark_copy pyspark_write sling spark"; \
		exit 1; \
	fi
	@echo "${GREEN}Running ETL benchmark: $(ETL)...${NC}"
	@bash run_tests.sh $(ETL)

build-all: ## Build all ETL Docker images
	@echo "${GREEN}Building all ETL Docker images...${NC}"
	@for dir in duckdb_copy duckdb_copy_parquet pandas_copy pandas_to_sql \
		pg_dump_restore polars_adbc_copy polars_connectorx_copy \
		polars_connectorx_write pyspark_copy pyspark_write sling spark; do \
		if [ -f "$$dir/Dockerfile" ]; then \
			echo "${GREEN}Building etl-$$dir...${NC}"; \
			docker build -t "etl-$$dir" "./$$dir" > /dev/null 2>&1 || \
				echo "${YELLOW}Warning: failed to build $$dir${NC}"; \
		fi; \
	done
	@echo "${GREEN}All images built${NC}"

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
