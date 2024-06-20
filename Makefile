.PHONY: lint

lint:
	pre-commit run --all-files


all: lint
