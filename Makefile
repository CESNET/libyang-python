# Copyright (c) 2018 Robin Jarry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

PYTHON ?= python3
define py_extension
from distutils.sysconfig import get_config_var
print("_libyang" + (get_config_var("EXT_SUFFIX") or get_config_var("SO")))
endef
py_extension := $(shell $(PYTHON) -c '$(py_extension)')

build: $(py_extension)

$(py_extension): build/clib/libyang.a $(wildcard cffi/*)
	$(PYTHON) ./setup.py build_ext --inplace

clib/CMakeLists.txt:
	git submodule update --init

build/clib/libyang.a: clib/CMakeLists.txt
	$(PYTHON) ./setup.py build_clib

sdist: clib/CMakeLists.txt
	rm -f dist/*.tar.gz
	$(PYTHON) ./setup.py sdist

wheel: build/clib/libyang.a
	rm -f dist/*.whl
	$(PYTHON) ./setup.py bdist_wheel

tests: $(py_extension)
	$(PYTHON) -m unittest discover -cv -s tests/ -t .

coverage: $(py_extension)
	$(PYTHON) -m coverage run -m unittest discover -cv -s tests/ -t .
	$(PYTHON) -m coverage html
	$(PYTHON) -m coverage report

upload: sdist wheel
	twine upload dist/*.tar.gz dist/*.whl

.PHONY: build sdist wheel upload tests
