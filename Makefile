# Copyright (c) 2018-2023 Robin Jarry
# SPDX-License-Identifier: MIT

all: lint tests

lint:
	tox -e lint

tests:
	tox -e py3

format:
	tox -e format

LYPY_COMMIT_RANGE ?= origin/master..

check-commits:
	./check-commits.sh $(LYPY_COMMIT_RANGE)

.PHONY: lint tests format check-commits
