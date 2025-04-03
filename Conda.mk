.DEFAULT_GOAL := help

ENV_NAME := core
PY_VERSION := "3.12"

# =============================================================================
# === (mini)Conda Targets.
# =============================================================================
##@ Conda
ccreate: ## Create Conda Environment.
	$(info Creating Conda Environment)
	@conda env create -f environment.yml
.PHONY: ccreate

cupdate: ## Update Conda Environment.
	$(info Updating Conda Environment)
	@conda env update --file environment.yml --prune
.PHONY: cupdate

cclone: ## Create an identical Environment on the same or another Machine.
	$(info Creating an identical Environment)
	@conda create --name $(ENV_NAME) --file spec-file.txt
.PHONY: cclone

# install: ## Install listed Packages into an existing Environment.
#   $(info Installing Conda Environment Packages)
#   @conda install --name $(ENV_NAME) --file spec-file.txt
# .PHONY: install

cactivate: ## Activate Conda Environment.
	$(info Activating Conda Environment)
	@conda activate $(ENV_NAME)
.PHONY: cactivate

cexport: ## Export Conda Environment.
	$(info Exporting Conda Environment)
	@conda env export > environment.yml
	@conda list --explicit > spec-file.txt
.PHONY: cexport

cremove: ## Remove Conda Environment.
	$(info Removing Conda Environment)
	@conda deactivate
	@conda remove --name $(ENV_NAME) --all
.PHONY: cremove

cupgrade: ## Upgrade Conda.
	$(info Upgrading Conda)
	@conda conda update --force conda
.PHONY: cupgrade
