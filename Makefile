# Copyright (c) 2020 CESNET, z.s.p.o.
# SPDX-License-Identifier: MIT
# Author David Sedlák


.PHONY: test

test:
	python -m unittest

coverage:
	python -m coverage run -m unittest discover -c tests/
	python -m coverage report
	python -m coverage html
