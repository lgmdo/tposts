.PHONY: test

DOCKER_SERVICE ?= tposts
TEST_PATH ?= src
PYTHON ?= poetry run python
MANAGE_PY := src/manage.py

## Run the test suite
test:
	@if [ "$(LOCAL)" = "true" ]; then \
        	echo "Running tests locally (LOCAL=true)"; \
        	$(PYTHON) $(MANAGE_PY) test $(TEST_PATH); \
    	else \
        	echo "Running tests in Docker (default)"; \
        	docker compose exec $(DOCKER_SERVICE) $(PYTHON) $(MANAGE_PY) test $(TEST_PATH); \
    	fi
