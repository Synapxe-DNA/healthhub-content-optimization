.PHONY: install lint

install:
	pip install -r requirements.txt

lint:
	pre-commit run --all-files


all: install lint
