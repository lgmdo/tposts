.PHONY: test type-check lint migrate

DOCKER_SERVICE ?= tposts
TEST_PATH ?= src
MANAGE_PY := src/manage.py

ifeq ($(LOCAL), true)
	POETRY ?= poetry
	RUNNING_MODE ?= locally
	REMOVE_MEDIA ?= rm -rf src/media
	DEBUG_PREFIX ?= DEBUG=true
else
	POETRY ?= docker compose exec tposts poetry
	RUNNING_MODE ?= in Docker
	REMOVE_MEDIA ?= docker compose exec tposts rm -rf src/media
	DEBUG_PREFIX ?=
endif

PYTHON ?= $(POETRY) run python
RUFF ?= $(POETRY) run ruff
PYRIGHT ?= $(POETRY) run pyright

test:
	@echo "running tests $(RUNNING_MODE)"
	@$(DEBUG_PREFIX) $(PYTHON) $(MANAGE_PY) test $(TEST_PATH);
	@$(REMOVE_MEDIA)

type-check:
	@echo "Running type-check $(RUNNING_MODE)"
	@$(PYRIGHT);

lint:
	@echo "Running lint $(RUNNING_MODE)"
	@$(RUFF) check;

migrate:
	@echo "Running migration $(RUNNING_MODE)"
	@$(PYTHON) $(MANAGE_PY) makemigrations
	@$(PYTHON) $(MANAGE_PY) migrate
