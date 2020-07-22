# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import re
from typing import Any, Dict, Iterator, List, Tuple, Union

from .keyed_list import KeyedList, py_to_yang


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


# -------------------------------------------------------------------------------------
def _xpath_keys_to_key_val(keys: List[Tuple[str, str]]) -> Union[str, Tuple[str, ...]]:
    """
    Extract key value from parsed xpath keys returned by xpath_split. The return value
    of this function can be used as argument to lookup elements in a KeyedList object.

    Examples:

    >>> _xpath_keys_to_key_val([('.', 'foo')])
    'foo'
    >>> _xpath_keys_to_key_val([('name', 'baz')])
    'baz'
    >>> _xpath_keys_to_key_val([('first-name', 'Charly'), ('last-name', 'Oleg')])
    ('Charly', 'Oleg')
    """
    if len(keys) == 1:
        return keys[0][1]
    return tuple(k[1] for k in keys)


# -------------------------------------------------------------------------------------
def _list_find_key_index(keys: List[Tuple[str, str]], lst: List) -> int:
    """
    Find the index of an element matching the parsed xpath keys returned by xpath_split
    into a native python list.

    :raises ValueError:
        If the element is not found.
    :raises TypeError:
        If the list elements are not dictionaries.
    """
    if keys[0][0] == ".":
        # leaf-list
        for i, elem in enumerate(lst):
            if py_to_yang(elem) == keys[0][1]:
                return i

    else:
        for i, elem in enumerate(lst):
            if not isinstance(elem, dict):
                raise TypeError("expected a dict")
            if all(k in elem and py_to_yang(elem[k]) == v for k, v in keys):
                return i

    raise ValueError("%s not found in list" % keys)


# -------------------------------------------------------------------------------------
def _xpath_find(data: Dict, xparts: List) -> Any:
    """
    Descend into a data dictionary.

    :arg data:
        The dictionary where to look for `xparts`.
    :arg xparts:
        Elements of an Xpath split with xpath_split()

    :returns:
        The element identified by `xparts`.
    :raises KeyError:
        If the element is not found in `data`.
    :raises TypeError:
        If `data` does not match the expected structure conveyed by `xparts`.
    """
    for _, name, keys in xparts:
        if not isinstance(data, dict):
            raise TypeError("expected a dict")
        if keys:
            lst = data[name]  # may raise KeyError
            if isinstance(lst, KeyedList):
                data = lst[_xpath_keys_to_key_val(keys)]  # shortcut, may raise KeyError

            elif isinstance(lst, list):
                # regular python list, need to iterate over it
                try:
                    i = _list_find_key_index(keys, lst)
                    data = lst[i]
                except ValueError:
                    # not found
                    raise KeyError(keys) from None

            else:
                raise TypeError("expected a list")

        else:
            data = data[name]  # may raise KeyError

    return data


# -------------------------------------------------------------------------------------
def xpath_get(data: Dict, xpath: str, default: Any = None) -> Any:
    """
    Get an element from a data structure (dict) that matches the given xpath.

    Examples:

    >>> config = {'conf': {'net': [{'name': 'mgmt', 'routing': {'a': 1}}]}}
    >>> xpath_get(config, '/prefix:conf/net[name="mgmt"]/routing')
    {'a': 1}
    >>> xpath_get(config, '/prefix:conf/net[name="prod"]/routing')
    >>> xpath_get(config, '/prefix:conf/net[name="prod"]/routing', {})
    {}
    """
    try:
        return _xpath_find(data, xpath_split(xpath))
    except KeyError:
        return default
