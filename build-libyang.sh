#!/bin/sh

set -e

die() {
	echo "error: $*"
	echo "usage: $0 [--static] --src=DIR --build=DIR [--install=DIR]"
	exit 1
} >&2

enable_static=OFF

for arg in "$@"; do
	case "$arg" in
	--static)
		enable_static=ON
		;;
	--src=*)
		src_dir=$(realpath -e ${arg#--src=})
		;;
	--build=*)
		build_dir=${arg#--build=}
		;;
	--install=*)
		install_dir=${arg#--install=}
		case "$install_dir" in
		/*)
			# absolute path, do nothing
			;;
		*)
			# relative path, convert to absolute
			install_dir="$PWD/$install_dir"
			;;
		esac
		;;
	*)
		die "Invalid argument: $arg"
		;;
	esac
done

if [ -z "$src_dir" ]; then
	die "Missing --src= argument"
fi
if [ -z "$build_dir" ]; then
	die "Missing --build= argument"
fi
if [ "$src_dir" = "$build_dir" ]; then
	die "Source and build directories must be different"
fi

mkdir -p "$build_dir"
cd "$build_dir"

cmake -DENABLE_STATIC=$enable_static \
	-DCMAKE_BUILD_TYPE=release \
	-DCMAKE_C_FLAGS=-fPIC \
	-DENABLE_BUILD_TESTS=OFF \
	-DENABLE_VALGRIND_TESTS=OFF \
	-DENABLE_CALGRIND_TESTS=OFF \
	-DCMAKE_INSTALL_PREFIX=${install_dir:-/} \
	-DGEN_LANGUAGE_BINDINGS=0 \
	"$src_dir"

make -j$(nproc)

if [ -n "$install_dir" ]; then
	make install
fi
