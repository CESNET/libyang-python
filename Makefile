# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

PYTHON ?= python3
define py_extension
from distutils.sysconfig import get_config_var
print("_libyang" + (get_config_var("EXT_SUFFIX") or get_config_var("SO")))
endef
py_extension := $(shell $(PYTHON) -c '$(py_extension)')
define buildtemp
import sys
from distutils.util import get_platform
print("build/temp." + get_platform() + "-{0}.{1}".format(*sys.version_info[:2]))
endef
buildtemp := $(shell $(PYTHON) -c '$(buildtemp)')

build: $(py_extension)

$(py_extension): $(buildtemp)/libyang.so $(wildcard cffi/*)
	$(PYTHON) ./setup.py build_ext --inplace

clib/CMakeLists.txt:
	git submodule update --init

$(buildtemp)/libyang.so: clib/CMakeLists.txt
	$(PYTHON) ./setup.py build_clib

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
