# Copyright (c) 2018-2023 Robin Jarry
# SPDX-License-Identifier: MIT

all: lint tests

lint:
	tox -e lint

tests:
	tox -e py3

format:
	tox -e format

LYPY_START_COMMIT ?= origin/master
LYPY_END_COMMIT ?= HEAD

check-commits:
	./check-commits.sh $(LYPY_START_COMMIT)..$(LYPY_END_COMMIT)

.PHONY: lint tests format check-commits
