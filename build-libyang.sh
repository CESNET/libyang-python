#!/bin/sh

set -e

die() {
	echo "error: $*"
	echo "usage: $0 --src=DIR --build=DIR [--install=DIR] [--prefix=DIR]"
	exit 1
} >&2

prefix_dir=/usr

for arg in "$@"; do
	case "$arg" in
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
	--prefix=*)
		prefix_dir=${arg#--prefix=}
		case "$prefix_dir" in
		/*)
			# absolute path, do nothing
			;;
		*)
			# relative path, convert to absolute
			prefix_dir="$PWD/$prefix_dir"
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

cmake -DCMAKE_BUILD_TYPE=release \
	-DENABLE_BUILD_TESTS=OFF \
	-DENABLE_VALGRIND_TESTS=OFF \
	-DENABLE_CALGRIND_TESTS=OFF \
	-DENABLE_BUILD_FUZZ_TARGETS=OFF \
	-DCMAKE_INSTALL_PREFIX=$prefix_dir \
	-DGEN_LANGUAGE_BINDINGS=0 \
	"$src_dir"

make -s -j$(nproc)

if [ -z "$install_dir" ]; then
	exit
fi

if [ "$install_dir" = "$prefix_dir" ]; then
	make -s install DESTDIR=/
else
	mkdir -p $install_dir/_include/libyang
	cp -a $src_dir/src/*.h ./src/*.h $install_dir/_include/libyang

	mkdir -p $install_dir/_lib
	cp -a ./libyang.so* $install_dir/_lib

	mkdir -p $install_dir/_lib/extensions
	cp -a ./src/extensions/*.so $install_dir/_lib/extensions

	mkdir -p $install_dir/_lib/user_types
	cp -a ./src/user_types/*.so $install_dir/_lib/user_types
fi
