.PHONY: install lint

install:
	pip install -r requirements.txt

lint:
	pre-commit run --all-files

#############################
# Commands to run docker
# for local development
#############################

.PHONY: local-db-start
local-db-start:
	@docker-compose --file ./docker/Dockercompose.yaml --env-file ./docker/dockercompose.env.local up hh-mongo -d


.PHONY: local-db-stop
local-db-stop:
	@docker-compose --file ./docker/Dockercompose.yaml --env-file ./docker/dockercompose.env.local down hh-mongo





all: lint
