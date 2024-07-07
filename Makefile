.PHONY: install lint lint-frontend clean-dry-run clean run local-db-start local-db-stop

install:
	pip install -r requirements.txt

lint:
	pre-commit run --all-files

lint-frontend:
	@cd ./frontend/app && npm run lint

DIRS ?= data/02_intermediate data/03_primary data/04_feature data/05_model_input data/06_models data/07_model_output

clean-dry-run:
	@echo "Cleaning"
	@cd content-optimization && \
	for dir in $(DIRS); do \
		echo "Would have cleaned $$dir"; \
	done
	@echo "Done!"

clean:
	@echo "Cleaning"
	@cd content-optimization && \
	for dir in $(DIRS); do \
		echo "Cleaned $$dir"; \
		find $$dir -mindepth 1 -type d -exec rm -rf {} +; \
	done
	@echo "Done!"

PIPELINE ?=

run:
	@cd content-optimization && \
	if [ -z "$(PIPELINE)" ]; then \
		kedro run; \
	else \
		kedro run --pipeline=$(PIPELINE); \
	fi

#############################
# Commands to run docker
# for local development
#############################

local-db-start:
	@docker-compose --file ./docker/Dockercompose.yaml --env-file ./docker/dockercompose.env.local up hh-mongo -d

local-db-stop:
	@docker-compose --file ./docker/Dockercompose.yaml --env-file ./docker/dockercompose.env.local down hh-mongo

all: install lint clean-dry-run clean run local-db-start local-db-stop
