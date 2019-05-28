#!/bin/sh

set -e

src="$1"
build="$2"
env="$3"
shift 3

if [ "$LIBYANG_INSTALL" = system ]; then
	"$(dirname $0)/build-libyang.sh" \
		--src="$src" --build="$build" --install="$env/opt"
	export LIBYANG_HEADERS=$env/opt/include
	export LIBYANG_LIBRARIES=$env/opt/lib
	export LIBYANG_EXTRA_LDFLAGS=-Wl,-rpath=$env/opt/lib
fi

python -m pip install "$@"
