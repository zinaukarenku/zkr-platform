.PHONY: all

all: pull release

pull:
	git pull

release:
	docker-compose up -d --build
