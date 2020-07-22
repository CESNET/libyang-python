# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import re
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

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
def _xpath_keys_to_key_name(
    keys: List[Tuple[str, str]]
) -> Optional[Union[str, Tuple[str, ...]]]:
    """
    Extract key name from parsed xpath keys returned by xpath_split. The return value
    of this function can be used as key_name argument when creating a new KeyedList
    object.

    Examples:

    >>> _xpath_keys_to_key_name([('.', 'foo')])
    # -> None
    >>> _xpath_keys_to_key_name([('name', 'baz')])
    'name'
    >>> _xpath_keys_to_key_name([('first-name', 'Charly'), ('last-name', 'Oleg')])
    ('first-name', 'last-name')
    """
    if keys[0][0] == ".":
        # leaf-list
        return None
    if len(keys) == 1:
        return keys[0][0]
    return tuple(k[0] for k in keys)


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
def _xpath_find(data: Dict, xparts: List, create_if_missing: bool = False) -> Any:
    """
    Descend into a data dictionary.

    :arg data:
        The dictionary where to look for `xparts`.
    :arg xparts:
        Elements of an Xpath split with xpath_split()
    :arg bool create_if_missing:
        If elements are missing from `data`, create them.

    :returns:
        The element identified by `xparts`.
    :raises KeyError:
        If create_if_missing=False and the element is not found in `data`.
    :raises TypeError:
        If `data` does not match the expected structure conveyed by `xparts`.
    """
    for _, name, keys in xparts:
        if not isinstance(data, dict):
            raise TypeError("expected a dict")
        if keys:
            if name not in data and create_if_missing:
                data[name] = KeyedList(key_name=_xpath_keys_to_key_name(keys))
            lst = data[name]  # may raise KeyError
            if isinstance(lst, KeyedList):
                try:
                    data = lst[_xpath_keys_to_key_val(keys)]
                except KeyError:
                    if not create_if_missing:
                        raise
                    data = dict(keys)
                    lst.append(data)

            elif isinstance(lst, list):
                # regular python list, need to iterate over it
                try:
                    i = _list_find_key_index(keys, lst)
                    data = lst[i]
                except ValueError:
                    # not found
                    if not create_if_missing:
                        raise KeyError(keys) from None
                    data = dict(keys)
                    lst.append(data)

            else:
                raise TypeError("expected a list")

        elif create_if_missing:
            data = data.setdefault(name, {})

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
        return _xpath_find(data, xpath_split(xpath), create_if_missing=False)
    except KeyError:
        return default


# -------------------------------------------------------------------------------------
def xpath_set(
    data: Dict, xpath: str, value: Any, force: bool = True, after: Optional[str] = None,
) -> Any:
    """
    Set the value pointed by the provided xpath into the provided data structure. If
    force=False and the value is already set in the data structure, do not overwrite it
    and return the current value.

    :arg data:
        The dictionary to update.
    :arg xpath:
        The path where to insert the value.
    :arg value:
        The value to insert in data.
    :arg force:
        Overwrite if a value already exists at the given xpath.
    :arg after:
        The element after which to insert the provided value. The meaning of this
        argument is similar to the prev_list argument of sr_get_change_tree_next:

        https://github.com/sysrepo/sysrepo/blob/v1.4.66/src/sysrepo.h#L1399-L1405

        `after=None`
            Append at the end of the list if not already present.
        `after=""`
            Insert at the beginning of the list if not already present.
        `after="foo"`
            Insert after the YANG leaf-list "foo" element. If "foo" element is not
            found, raise a ValueError.
        `after="[key1='value1']..."`
            Insert after the YANG list element with matching keys. If such element is
            not found, raise a ValueError.

        If the value identified by `xpath` already exists in data, the `after` argument
        is ignored. If force=True, the existing value is replaced (at its current
        position in the list), otherwise the existing value is returned.

    :returns:
        The inserted value or the existing value if force=False and a value already
        exists a the given xpath.
    :raises ValueError:
        If `after` is specified and no matching element to insert after is found.

    Examples:

    >>> state = {'state': {'vrf': [{'name': 'vr0', 'routing': {'a': 1}}]}}
    >>> xpath_set(state, '/state/vrf[name="vr0"]/routing/b', 55)
    55
    >>> state
    {'state': {'vrf': [{'name': 'vr0', 'routing': {'a': 1, 'b': 55}}]}}
    >>> xpath_set(state, '/state/vrf[name="vr0"]/routing', {'c': 8})
    {'a': 1, 'b': 55}
    >>> state
    {'state': {'vrf': [{'name': 'vr0', 'routing': {'a': 1, 'b': 55}}]}}
    """
    parts = list(xpath_split(xpath))
    parent = _xpath_find(data, parts[:-1], create_if_missing=True)
    _, name, keys = parts[-1]

    if not keys:
        # name points to a container or leaf, trivial
        if force:
            parent[name] = value
            return value
        return parent.setdefault(name, value)

    # list or leaf-list
    if name not in parent:
        if after is not None:
            parent[name] = []
        else:
            parent[name] = KeyedList(key_name=_xpath_keys_to_key_name(keys))

    lst = parent[name]

    if isinstance(lst, KeyedList):
        # shortcut access is possible
        if after is not None:
            raise ValueError("after='...' is not supported for unordered lists")
        key_val = _xpath_keys_to_key_val(keys)
        if key_val in lst:
            if force:
                del lst[key_val]
                lst.append(value)
        else:
            lst.append(value)
        return lst[key_val]

    if isinstance(lst, list):
        # regular python list, need to iterate over it
        try:
            i = _list_find_key_index(keys, lst)
            # found
            if force:
                lst[i] = value
            return lst[i]
        except ValueError:
            # not found
            if after is None:
                lst.append(value)
            elif after == "":
                lst.insert(0, value)
            else:
                if after[0] != "[":
                    after = "[.=%r]" % str(after)
                _, _, after_keys = next(xpath_split("/*" + after))
                insert_index = _list_find_key_index(after_keys, lst) + 1
                if insert_index == len(lst):
                    lst.append(value)
                else:
                    lst.insert(insert_index, value)
            return value

    raise TypeError("expected a list")


# -------------------------------------------------------------------------------------
def xpath_setdefault(data: Dict, xpath: str, default: Any) -> Any:
    """
    Shortcut for xpath_set(..., force=False).
    """
    return xpath_set(data, xpath, default, force=False)
