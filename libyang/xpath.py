# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import re
from typing import Iterator, List, Tuple


# -------------------------------------------------------------------------------------
XPATH_ELEMENT_RE = re.compile(r"^/(?:(?P<prefix>[-\w]+):)?(?P<name>[-\w\*]+)")


def xpath_split(xpath: str) -> Iterator[Tuple[str, str, List[Tuple[str, str]]]]:
    """
    Return an iterator that yields xpath components:

        (prefix, name, keys)

    Where:

        :var prefix:
            The YANG prefix where ``name`` is defined. May be ``None`` if no prefix is
            specified.
        :var name:
            The name of the YANG element (container, list, leaf, leaf-list).
        :var keys:
            A list of tuples ``("key_name", "key_value")`` parsed from Xpath key
            specifiers: ``[key_name="key_value"]...``.

    Example:

    >>> list(xpath_split("/p1:a/b/c[k='v']/p2:d"))
    [("p1", "a", []), (None, "b", []), (None, "c", [("k", "v")]), ("p2", "d", [])]
    """
    xpath = xpath.strip()
    if not xpath:
        raise ValueError("empty xpath")
    if xpath[0] != "/":
        # support relative xpaths
        xpath = "/" + xpath
    i = 0

    while i < len(xpath):
        match = XPATH_ELEMENT_RE.search(xpath[i:])
        if not match:
            raise ValueError(
                "invalid xpath: %r (expected r'%s' at index %d)"
                % (xpath, XPATH_ELEMENT_RE.pattern, i)
            )
        prefix, name = match.groups()
        i += match.end()

        keys = []
        while i < len(xpath) and xpath[i] == "[":
            i += 1  # skip opening '['
            j = xpath.find("=", i)  # find key name end
            key_name = xpath[i:j]
            quote = xpath[j + 1]  # record opening quote character
            j = i = j + 2  # skip '=' and opening quote
            while True:
                if xpath[j] == "\\":
                    j += 1  # skip escaped character
                elif xpath[j] == quote:
                    break  # end of key value
                j += 1
            # replace escaped chars by their non-escape version
            key_value = xpath[i:j].replace("\\", "")
            keys.append((key_name, key_value))
            i = j + 2  # skip closing quote and ']'

        yield prefix, name, keys
