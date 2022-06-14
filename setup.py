#!/usr/bin/env python3
# Copyright (c) 2018-2020 Robin Jarry
# SPDX-License-Identifier: MIT

import datetime
import os
import re
import subprocess

import setuptools
import setuptools.command.sdist


# -------------------------------------------------------------------------------------
if os.environ.get("LIBYANG_INSTALL", "system") == "embed":
    raise NotImplementedError(
        "LIBYANG_INSTALL=embed is no longer supported. "
        "Please install libyang separately first."
    )


# -------------------------------------------------------------------------------------
def git_describe_to_pep440(version):
    """
    ``git describe`` produces versions in the form: `v0.9.8-20-gf0f45ca` where
    20 is the number of commit since last release, and gf0f45ca is the short
    commit id preceded by 'g' we parse this a transform into a pep440 release
    version 0.9.9.dev20 (increment last digit and add dev before 20)
    """
    match = re.search(
        r"""
        v(?P<major>\d+)\.
        (?P<minor>\d+)\.
        (?P<patch>\d+)
        ((\.post|-)(?P<post>\d+)(?!-g))?
        ([\+~](?P<local_segment>.*?))?
        (-(?P<dev>\d+))?(-g(?P<commit>.+))?
        """,
        version,
        flags=re.VERBOSE,
    )
    if not match:
        raise ValueError("unknown tag format")
    dic = {
        "major": int(match.group("major")),
        "minor": int(match.group("minor")),
        "patch": int(match.group("patch")),
    }
    fmt = "{major}.{minor}.{patch}"
    if match.group("dev"):
        dic["patch"] += 1
        dic["dev"] = int(match.group("dev"))
        fmt += ".dev{dev}"
    elif match.group("post"):
        dic["post"] = int(match.group("post"))
        fmt += ".post{post}"
    if match.group("local_segment"):
        dic["local_segment"] = match.group("local_segment")
        fmt += "+{local_segment}"
    return fmt.format(**dic)


# -------------------------------------------------------------------------------------
def get_version_from_archive_id(git_archive_id="$Format:%ct %d$"):
    """
    Extract the tag if a source is from git archive.

    When source is exported via `git archive`, the git_archive_id init value is
    modified and placeholders are expanded to the "archived" revision:

        %ct: committer date, UNIX timestamp
        %d: ref names, like the --decorate option of git-log

    See man gitattributes(5) and git-log(1) (PRETTY FORMATS) for more details.
    """
    # mangle the magic string to make sure it is not replaced by git archive
    if git_archive_id.startswith("$For" "mat:"):  # pylint: disable=implicit-str-concat
        raise ValueError("source was not modified by git archive")

    # source was modified by git archive, try to parse the version from
    # the value of git_archive_id
    match = re.search(r"tag:\s*([^,)]+)", git_archive_id)
    if match:
        # archived revision is tagged, use the tag
        return git_describe_to_pep440(match.group(1))

    # archived revision is not tagged, use the commit date
    tstamp = git_archive_id.strip().split()[0]
    d = datetime.datetime.utcfromtimestamp(int(tstamp))
    return d.strftime("2.%Y.%m.%d")


# -------------------------------------------------------------------------------------
def read_file(fpath, encoding="utf-8"):
    with open(fpath, "r", encoding=encoding) as f:
        return f.read().strip()


# -------------------------------------------------------------------------------------
def get_version():
    try:
        return read_file("libyang/VERSION")
    except IOError:
        pass

    if "LIBYANG_PYTHON_FORCE_VERSION" in os.environ:
        return os.environ["LIBYANG_PYTHON_FORCE_VERSION"]

    try:
        return get_version_from_archive_id()
    except ValueError:
        pass

    try:
        if os.path.isdir(".git"):
            out = subprocess.check_output(
                ["git", "describe", "--tags", "--always"], stderr=subprocess.DEVNULL
            )
            return git_describe_to_pep440(out.decode("utf-8").strip())
    except Exception:
        pass

    return "2.99999.99999"


# -------------------------------------------------------------------------------------
class SDistCommand(setuptools.command.sdist.sdist):
    def write_lines(self, file, lines):
        with open(file, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

    def make_release_tree(self, base_dir, files):
        super().make_release_tree(base_dir, files)
        version_file = os.path.join(base_dir, "libyang/VERSION")
        self.execute(
            self.write_lines,
            (version_file, [self.distribution.metadata.version]),
            "Writing %s" % version_file,
        )


# -------------------------------------------------------------------------------------
setuptools.setup(
    name="libyang",
    version=get_version(),
    description="CFFI bindings to libyang",
    long_description=read_file("README.rst"),
    url="https://github.com/CESNET/libyang-python",
    license="MIT",
    author="Robin Jarry",
    author_email="robin@jarry.cc",
    keywords=["libyang", "cffi"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
    ],
    packages=["libyang"],
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.6",
    setup_requires=["setuptools", 'cffi; platform_python_implementation != "PyPy"'],
    install_requires=['cffi; platform_python_implementation != "PyPy"'],
    cffi_modules=["cffi/build.py:BUILDER"],
    cmdclass={"sdist": SDistCommand},
)
