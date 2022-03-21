#!/bin/sh
# Copyright (c) 2020 Robin Jarry
# SPDX-License-Identifier: MIT

set -e

venv="$1"
shift 1

download()
{
	url="$1"
	branch="$2"
	dir="$3"
	if which git >/dev/null 2>&1; then
		git clone --single-branch --branch "$branch" --depth 1 \
			"$url.git" "$dir"
	elif which curl >/dev/null 2>&1; then
		mkdir -p "$dir"
		curl -L "$url/archive/$branch.tar.gz" | \
			tar --strip-components=1 -zx -C "$dir"
	elif which wget >/dev/null 2>&1; then
		mkdir -p "$dir"
		wget -O - "$url/archive/$branch.tar.gz" | \
			tar --strip-components=1 -zx -C "$dir"
	else
		echo "ERROR: neither git nor curl nor wget are available" >&2
		exit 1
	fi
}

# build and install libyang into the virtualenv
src="${LIBYANG_SRC:-$venv/.src}"
if ! [ -d "$src" ]; then
	libyang_branch="${LIBYANG_BRANCH:-master}"
	download "https://github.com/CESNET/libyang" "$libyang_branch" "$src"
fi

prefix="$venv/.ly"

build="$venv/.build"
mkdir -p "$build"
cmake -DCMAKE_BUILD_TYPE=debug \
	-DENABLE_BUILD_TESTS=OFF \
	-DENABLE_VALGRIND_TESTS=OFF \
	-DENABLE_CALGRIND_TESTS=OFF \
	-DENABLE_BUILD_FUZZ_TARGETS=OFF \
	-DCMAKE_INSTALL_PREFIX="$prefix" \
	-DCMAKE_INSTALL_LIBDIR=lib \
	-DGEN_LANGUAGE_BINDINGS=OFF \
	-H"$src" -B"$build"
make --no-print-directory -C "$build" -j`nproc`
make --no-print-directory -C "$build" install

prefix=$(readlink -ve $prefix)

LIBYANG_HEADERS="$prefix/include" \
LIBYANG_LIBRARIES="$prefix/lib" \
LIBYANG_EXTRA_LDFLAGS="-Wl,--enable-new-dtags,-rpath=$prefix/lib" \
	python -m pip install "$@"
