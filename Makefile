.PHONY: install lint clean-dry-run clean run run-data-processing run-feature-engineering local-db-start local-db-stop

install:
	pip install -r requirements.txt

lint:
	pre-commit run --all-files

clean-dry-run:
	cd content-optimization && \
		find data/02_intermediate -mindepth 1 -type d -print && \
		find data/03_primary -mindepth 1 -type d -print && \
		find data/04_feature -mindepth 1 -type d -print

clean:
	cd content-optimization && \
		find data/02_intermediate -mindepth 1 -type d -exec rm -rf {} + && \
		find data/03_primary -mindepth 1 -type d -exec rm -rf {} + && \
		find data/04_feature -mindepth 1 -type d -exec rm -rf {} +

run:
	cd content-optimization && \
		kedro run

run-data-processing:
	cd content-optimization && \
		kedro run --pipeline=data_processing

run-feature-engineering:
	cd content-optimization && \
		kedro run --pipeline=feature_engineering

#############################
# Commands to run docker
# for local development
#############################

local-db-start:
	@docker-compose --file ./docker/Dockercompose.yaml --env-file ./docker/dockercompose.env.local up hh-mongo -d

local-db-stop:
	@docker-compose --file ./docker/Dockercompose.yaml --env-file ./docker/dockercompose.env.local down hh-mongo

all: install lint clean-dry-run clean run run-data-processing run-feature-engineering local-db-start local-db-stop
