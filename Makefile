.PHONY: test type-check lint

DOCKER_SERVICE ?= tposts
TEST_PATH ?= src
MANAGE_PY := src/manage.py

ifeq ($(LOCAL), true)
	POETRY ?= poetry
	RUNNING_MODE ?= locally
else
	POETRY ?= docker compose up exec poetry
	RUNNING_MODE ?= in Docker
endif

PYTHON ?= $(POETRY) run python
RUFF ?= $(POETRY) run ruff
PYRIGHT ?= $(POETRY) run pyright

test:
	@echo "Running test $(RUNNING_MODE)"
	@$(PYTHON) $(MANAGE_PY) test $(TEST_PATH);

type-check:
	@echo "Running type-check $(RUNNING_MODE)"
	@$(PYRIGHT);

lint:
	@echo "Running lint $(RUNNING_MODE)"
	@$(RUFF) check;




