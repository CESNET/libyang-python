# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

from collections.abc import Hashable
import copy
from typing import Any, Iterable, Optional, Tuple, Union


# -------------------------------------------------------------------------------------
ListKeyVal = Union[str, Tuple[str, ...]]


class KeyedList(list):
    """
    YANG lists are not ordered by default but indexed by keys. This class mimics some
    parts of the list API but allows direct access to elements when their keys are
    known.

    Note that even though this class inherits from list, it is not really a list.
    Internally, it behaves as a dict. Some parts of the list API that assume any
    ordering are not supported for that reason.

    The inheritance is only to avoid confusion and make isinstance return something that
    looks like a list.
    """

    def __init__(
        self,
        init: Iterable = None,
        key_name: Optional[Union[str, Tuple[str, ...]]] = None,
    ) -> None:
        """
        :arg init:
            Values to initialize the list with.
        :arg key_name:
            Name of keys in the element when the element is a dict. If there is only one
            key, it is a plain string, if there is more than one key, it is a tuple of
            strings. If there is no key (leaf-list), key_name is None.
        """
        super().__init__()  # this is not a real list anyway
        self._key_name = key_name
        self._map = {}  # type: Dict[ListKeyVal, Any]
        if init is not None:
            self.extend(init)

    def _element_key(self, element: Any) -> Hashable:
        if self._key_name is None:
            return py_to_yang(element)
        if not isinstance(element, dict):
            raise TypeError("element must be a dict")
        if isinstance(self._key_name, str):
            return py_to_yang(element[self._key_name])
        return tuple(py_to_yang(element[k]) for k in self._key_name)

    def clear(self) -> None:
        self._map.clear()

    def copy(self) -> "KeyedList":
        return KeyedList(self._map.values(), key_name=self._key_name)

    def append(self, element: Any) -> None:
        key = self._element_key(element)
        if key in self._map:
            raise ValueError("element with key %r already in list" % (key,))
        self._map[key] = element

    def extend(self, iterable: Iterable) -> None:
        for element in iterable:
            self.append(element)

    def pop(self, key: ListKeyVal = None, default: Any = None) -> Any:
        if key is None or isinstance(key, (int, slice)):
            raise TypeError("non-ordered lists cannot be accessed by index")
        return self._map.pop(key, default)

    def remove(self, element: Any) -> None:
        key = self._element_key(element)
        del self._map[key]

    def __getitem__(self, key: ListKeyVal) -> Any:
        if isinstance(key, (int, slice)):
            raise TypeError("non-ordered lists cannot be accessed by index")
        return self._map[key]

    def __delitem__(self, key: ListKeyVal) -> None:
        if isinstance(key, (int, slice)):
            raise TypeError("non-ordered lists cannot be accessed by index")
        del self._map[key]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, KeyedList):
            return other._map == self._map
        if not isinstance(other, list):
            return False
        try:
            other_map = {}
            for e in other:
                other_map[self._element_key(e)] = e
            return other_map == self._map
        except (KeyError, TypeError):
            return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __iter__(self):
        return iter(self._map.values())

    def __len__(self):
        return len(self._map)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(list(self._map.values()))

    def count(self, element: Any):
        if element in self:
            return 1
        return 0

    def __contains__(self, element: Any) -> bool:
        try:
            if isinstance(element, dict) or element not in self._map:
                key = self._element_key(element)
            else:
                key = element
            return key in self._map
        except (KeyError, TypeError):
            return False

    def __copy__(self) -> "KeyedList":
        return self.copy()

    def __deepcopy__(self, memo) -> "KeyedList":
        k = KeyedList.__new__(KeyedList)
        memo[id(self)] = k
        k._key_name = copy.deepcopy(self._key_name, memo)
        k._map = copy.deepcopy(self._map, memo)
        return k

    # unsupported list API methods
    def __unsupported(self, *args, **kwargs):
        raise TypeError("unsupported operation for non-ordered lists")

    index = __unsupported
    insert = __unsupported
    reverse = __unsupported
    sort = __unsupported
    __add__ = __unsupported
    __ge__ = __unsupported
    __gt__ = __unsupported
    __iadd__ = __unsupported
    __imul__ = __unsupported
    __le__ = __unsupported
    __lt__ = __unsupported
    __mul__ = __unsupported
    __reversed__ = __unsupported
    __rmul__ = __unsupported
    __setitem__ = __unsupported


# -------------------------------------------------------------------------------------
def py_to_yang(val: Any) -> str:
    """
    Convert a python value to a string following how it would be stored in a libyang
    data tree. Also suitable for comparison with YANG list keys (which are always
    strings).
    """
    if isinstance(val, str):
        return val
    if val is True:
        return "true"
    if val is False:
        return "false"
    return str(val)
