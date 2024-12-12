.DEFAULT_GOAL := help

SHELL := /bin/bash
WORKDIR := .
ENVDIR := $(WORKDIR)/.env

COMPOSE_SERVICE_NAME := "privateurl"

DOCKER_RUN := "docker-compose exec privateurl python"
LOCAL_RUN := "python"

# =============================================================================
# === Detect OS, and set appropriate Environment Variables.
# =============================================================================
ifeq ($(OS), Windows_NT)
	SHELL := /bin/bash
	INIT := python -m venv .env
	ENV := $(ENVDIR)/Scripts
	ACTIVATE := . $(ENV)/activate
	UPIP := $(ENV)/python.exe -m pip install --upgrade pip
else
	SHELL := /bin/bash
	INIT := virtualenv .env
	ENV := $(ENVDIR)/bin
	ACTIVATE := . $(ENV)/activate
	UPIP := $(ENV)/pip install -U  pip

	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S), Linux)
		# Do something
	endif
	ifeq ($(UNAME_S), Darwin)
		# Do something
	endif
endif

$(info Detected OS: $(OS))

# =============================================================================
# === Set-up Targets.
# =============================================================================
##@ Set-up
setup: ## Initiate Virtual Environment.
	$(info Initiating Virtual Environment)
	@pip install virtualenv
	$(INIT)
.PHONY: setup

env: setup ## Activate Virtual Environment.
	$(info Activating Virtual Environment)
	$(ACTIVATE)
.PHONY: env

install: env requirements.txt ## Install Requirements.
	$(info Installing Requirements)
	$(UPIP)
	$(ENV)/pip install -Ur requirements.txt --no-cache-dir
.PHONY: install

# =============================================================================
# === Development Targets.
# =============================================================================
##@ Development
test: run migrate ## Run Tests.
	$(info Running Tests)
	ifeq ($(OS), Windows_NT)
		@docker-compose exec $(COMPOSE_SERVICE_NAME) coverage run --source="." ./manage.py test --settings=settings.testing && coverage report -m --skip-empty && coverage html --skip-empty
	else
		@docker-compose -exec $(COMPOSE_SERVICE_NAME) --rm --user $(UID):`id -g` coverage run --source="." ./manage.py test --settings=settings.testing && coverage report -m --skip-empty && coverage html --skip-empty
	endif
.PHONY: test

# test-local: run-local migrate ## Run Tests.
test-local: run-local ## Run Tests.
	$(info Running Tests)
	@python manage.py migrate
	$(ENV)/coverage run --source="." ./manage.py test --settings=settings.testing
	$(ENV)/coverage report -m --skip-empty
	$(ENV)/coverage html --skip-empty
.PHONY: test-local

lint: install ## Run Linter.
	$(info Running Linter)
	$(ENV)/pylint privateurl/ settings/ setup.py --reports=y > reports/pylint.report
.PHONY: lint

# =============================================================================
# === Clean-up Targets.
# =============================================================================
##@ Clean-up
mostly-clean: ## Stop/remove all the locally created Containers, and Volumes.
	$(info Cleaning up Things)
	@docker-compose down --rmi local -v --remove-orphans
.PHONY: mostly-clean

clean: mostly-clean ## Stop/remove all the locally built Images, Containers, and Volumes; clean up the Project Folders.
	$(info Cleaning up Things)
	@rm -rf __pycache__
	@rm -rf *.pyc
	@rm -rf .env
.PHONY: clean

prune: clean ## Do a System Prune to remove untagged and unused Images/Containers.
	$(info Doing a System Prune)
	@docker system prune -af
	@docker volume prune -af
.PHONY: prune

# =============================================================================
# === CI/CD Targets.
# =============================================================================
##@ CI/CD
login: ## Login the Docker Daemon to AWS ECR.
	$(info Logging the Docker Daemon to AWS ECR.)
.PHONY: login

build: login ## Build the Containers/Images, defined in the `docker-compose`.
	$(info Building the Containers/Images)
	@docker-compose -f docker-compose.yml build --pull $(COMPOSE_SERVICE_NAME)
	@docker-compose -f docker-compose.yml --compatibility up --no-start
.PHONY: build

run: build ## Start the Compose.
	$(info Starting the Compose)
	@docker-compose -f docker-compose.yml up # -d
.PHONY: run

run-local: install ## Start the Compose, bypassing Build Steps.
	$(info Starting the Compose)
	@docker-compose -f docker-compose.local.yml up -d
.PHONY: run-local

down: ## Clean up the Project Folders.
	$(info Cleaning Things )
	@docker-compose down
.PHONY: down

migrate:
	$(info Migrating)
	@docker-compose exec privateurl python manage.py migrate
.PHONY: migrate

# =============================================================================
# === Helpers Targets.
# =============================================================================
##@ Helpers
help: ## Display this Help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
.PHONY: help
