.EXPORT_ALL_VARIABLES:
COMPOSE_FILE ?= ./build/docker-compose/docker-compose.yml
SERVICE_NAME ?= fastapi-template
ALEMBIC_CONFIG = src/alembic.ini

-include .$(PWD)/.env

.PHONY: help
help: # Display available commands
	@echo "\n\033[0;33mAvailable make commands:\033[0m\n"
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: start
start: build up # Build and spin up the application in one command

.PHONY: restart
restart: down up # Restart the application

.PHONY: up
up:  # Spin up the application
	docker compose -f $(COMPOSE_FILE) up -d
	docker compose ps

.PHONY: down
down: # Shut down the application
	docker compose down

.PHONY: logs
logs: # Follow logs of all running containers
	docker compose logs --follow

.PHONY: connect
connect: # Connect to the running sbxc-be container
	docker compose exec -it $(SERVICE_NAME) /bin/bash

.PHONY: run-linters
run-linters: run-black run-ruff # Run black & ruff linters

.PHONY: run-black
run-black: # Run black linter
	docker compose exec $(SERVICE_NAME) black .

.PHONY: run-ruff
run-ruff: # Run ruff linter
	docker compose exec $(SERVICE_NAME) ruff check --fix --unsafe-fixes .

.PHONY: test
test: # Run tests
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pytest tests/.

.PHONY: show-cov-report
show-cov-report: # Displays coverage report from the last pytest run
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) coverage report --show-missing --fail-under $(COVERAGE_MINIMUM_PERCENT)

.PHONY: build
build: # Build docker image of the application
	docker build --tag=$(SERVICE_NAME) --file=build/docker/Dockerfile .
