.PHONY: install install-dev test run
.PHONY: docker-build docker-run docker-rerun docker-stop docker-clean docker-rebuild

###########################
### LOCAL DEVELOPMENT #####
###########################

install:
	pip install .

install-dev:
	pip install ".[test]"

test:
	pytest tests

run:
	uvicorn src.main:app --reload

###########################
###### DOCKER PART #######
###########################

docker-build:
	docker build -t eich-crud .

docker-run:
	docker run \
		--name eich-container \
		--add-host=host.docker.internal:host-gateway \
		-p 8054:8054 \
		-e DATABASE_URL="postgresql+psycopg://kubsu:kubsu@host.docker.internal:5432/kubsu" \
		eich-crud

docker-rerun: docker-stop docker-run
	@echo "Container restarted successfully"

docker-stop:
	-docker stop eich-container
	-docker rm eich-container

docker-clean: docker-stop
	-docker rmi eich-crud
	-docker system prune -f

docker-rebuild: docker-clean docker-build docker-run
	@echo "Full rebuild completed"
