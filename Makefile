# Copyright (c) 2018-2020 Robin Jarry
# SPDX-License-Identifier: MIT

PYTHON ?= python3
define py_extension
from distutils.sysconfig import get_config_var
print("_libyang" + (get_config_var("EXT_SUFFIX") or get_config_var("SO")))
endef
py_extension := $(shell $(PYTHON) -c '$(py_extension)')

build: $(py_extension)

$(py_extension): libyang/_lib/libyang.so libyang/_include/libyang/libyang.h $(wildcard cffi/*)
	LIBYANG_INSTALL=embed $(PYTHON) ./setup.py build_ext --inplace

libyang/_lib/libyang.so libyang/_include/libyang/libyang.h: clib/CMakeLists.txt
	LIBYANG_INSTALL=embed $(PYTHON) ./setup.py build_clib

clib/CMakeLists.txt:
	git submodule update --init

sdist: clib/CMakeLists.txt
	rm -f dist/*.tar.gz
	$(PYTHON) ./setup.py sdist

tests: $(py_extension)
	$(PYTHON) -m unittest discover -cv -s tests/ -t .

coverage: $(py_extension)
	$(PYTHON) -m coverage run -m unittest discover -cv -s tests/ -t .
	$(PYTHON) -m coverage html
	$(PYTHON) -m coverage report

upload: sdist
	twine upload dist/*.tar.gz

.PHONY: build sdist upload tests
