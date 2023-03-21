#* Variables
PYTHON ?= python
PYTHONPATH := `pwd`

#* Docker variables
IMAGE := simple_css_selector_transform
VERSION := latest

#* Poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://install.python-poetry.org | "$(PYTHON)" -

.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://install.python-poetry.org | "$(PYTHON)" - --uninstall

#* Installation
.PHONY: install
install:
	poetry install --sync
	poetry export --without-hashes > requirements.txt
	-poetry run mypy --install-types ./

.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install

#* Formatters
.PHONY: format
codestyle:
	poetry run pyupgrade --exit-zero-even-if-changed --py38-plus **/*.py
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

.PHONY: format
format: codestyle

#* Linting
.PHONY: test
test:
	poetry run pytest -c pyproject.toml --cov-report=html --cov=simple_css_selector_transform tests/
	poetry run coverage-badge -o assets/images/coverage.svg -f

.PHONY: check-codestyle
check-codestyle:
	poetry run isort --diff --check-only --settings-path pyproject.toml ./
	poetry run black --diff --check --config pyproject.toml ./
	poetry run darglint --verbosity 2 simple_css_selector_transform tests

.PHONY: mypy
mypy:
	poetry run mypy --config-file pyproject.toml ./

.PHONY: check-safety
check-safety:
	poetry check
	poetry run safety check --full-report
	poetry run bandit -ll --recursive simple_css_selector_transform tests

.PHONY: lint
lint: check-codestyle mypy test check-safety

.PHONY: update-dev-deps
update-dev-deps:
	poetry add -D              \
		pytest-cov@latest      \
		coverage-badge@latest  \
		pytest-html@latest     \
		coverage@latest        \
		safety@latest          \
		pyupgrade@latest       \
		pytest@latest          \
		"isort[colors]@latest" \
		bandit@latest          \
		darglint@latest        \
		mypy@latest            \
		pre-commit@latest      \
		pydocstyle@latest      \
		pylint@latest

#* Docker
# Example: make docker-build VERSION=latest
# Example: make docker-build IMAGE=some_name VERSION=0.1.0
.PHONY: docker-build
docker-build:
	@echo Building docker $(IMAGE):$(VERSION) ...
	docker build \
		-t $(IMAGE):$(VERSION) . \
		-f ./docker/Dockerfile --no-cache

# Example: make docker-remove VERSION=latest
# Example: make docker-remove IMAGE=some_name VERSION=0.1.0
.PHONY: docker-remove
docker-remove:
	@echo Removing docker $(IMAGE):$(VERSION) ...
	docker rmi -f $(IMAGE):$(VERSION)

#* Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: dsstore-remove
dsstore-remove:
	find . | grep -E ".DS_Store" | xargs rm -rf

.PHONY: mypycache-remove
mypycache-remove:
	find . | grep -E ".mypy_cache" | xargs rm -rf

.PHONY: ipynbcheckpoints-remove
ipynbcheckpoints-remove:
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

.PHONY: pytestcache-remove
pytestcache-remove:
	find . | grep -E ".pytest_cache" | xargs rm -rf

.PHONY: cleanup
cleanup: pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove
