.PHONY: \
	all install run

all: .make-install

install: .make-install

.make-install-pipenv:
	@if ! which pipenv &> /dev/null; then \
		pip install pipenv; \
	fi
	@touch $@

.make-install: Pipfile .make-install-pipenv
	pipenv install -d
	@touch $@

run: .make-install
	python3 -m src.skill_newyear_quest.application

flake:
	flake8 src/skill_newyear_quest
	flake8 src/tests

mypy:
	mypy src/skill_newyear_quest

isort:
	isort setup.py
	isort src/skill_newyear_quest
	isort src/tests

test:
	pytest -q src/tests --log-format="%(asctime)s %(levelname)s %(message)s" --log-date-format="%Y-%m-%d %H:%M:%S"
