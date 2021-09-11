# Copyright (c) 2018-2020 Robin Jarry
# SPDX-License-Identifier: MIT

all: lint tests

lint:
	tox -e lint

tests:
	tox -e py3-libyang1

format:
	tox -e format

.PHONY: lint tests format
