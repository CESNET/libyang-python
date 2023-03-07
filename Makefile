# Copyright (c) 2018-2023 Robin Jarry
# SPDX-License-Identifier: MIT

all: lint tests

lint:
	tox -e lint

tests:
	tox -e py3

format:
	tox -e format

.PHONY: lint tests format
