.PHONY: install lint clean-dry-run clean run test local-db-start local-db-stop

install:
	pip install -r requirements.txt

lint:
	pre-commit run --all-files


# List of directories to operate on
DIRS ?= data/02_intermediate data/03_primary data/04_feature data/05_model_input data/06_models data/07_model_output

clean-dry-run:
	@python script.py --dry-run --dirs $(DIRS)

clean:
	@python script.py --dirs $(DIRS)


PIPELINE ?=

run:
	@cd content-optimization && \
	if [ -z "$(PIPELINE)" ]; then \
		kedro run; \
	else \
		kedro run --pipeline=$(PIPELINE); \
	fi


test:
	@python run_tests.py --files $(FILES) --functions $(FUNCTIONS)


#############################
# Commands to run docker
# for local development
#############################

local-db-start:
	@docker-compose --file ./docker/Dockercompose.yaml --env-file ./docker/dockercompose.env.local up hh-mongo -d

local-db-stop:
	@docker-compose --file ./docker/Dockercompose.yaml --env-file ./docker/dockercompose.env.local down hh-mongo

all: install lint clean-dry-run clean run test local-db-start local-db-stop
