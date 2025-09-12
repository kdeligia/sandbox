from dataclasses import dataclass
from typing import Any, Hashable

_EMPTY = object()
_DELETED = object()


@dataclass
class _Entry:
    key: object
    value: object
    h: int


class OpenAddressingHashTable:
    """
    Open-addressing hash table with linear probing and power-of-two capacity.
    - Insert overwrites existing values for the same key.
    - Automatic resizing keeps load factor under a target for stable performance.
    """

    # Potential improvement: use __slots__ to populate attributes instead of having a __dict__ for each
    # instance.

    def __init__(self, initial_capacity: int = 8, max_load: float = 0.70):
        self._capacity = self._next_pow2(max(8, initial_capacity))
        self._storage: list[object | _Entry] = [_EMPTY] * self._capacity
        self._mask = self._capacity - 1
        self._size = 0
        self._max_load = max_load
        self._resize_threshold = int(self._capacity * self._max_load)
        self._deleted_count = 0
        self._deleted_clean_ratio = 0.3

    def insert(self, key: Hashable, value: Any):
        self._maybe_grow_or_clean()

        h = hash(key)
        target_index = h & self._mask
        # NOTE: This is equivalent to h % self._capacity
        # if self._capacity = 2^n.

        first_deletion_index = None
        while True:
            target_slot = self._storage[target_index]
            if target_slot is _EMPTY:
                target_index = (
                    first_deletion_index
                    if first_deletion_index is not None
                    else target_index
                )
                self._storage[target_index] = _Entry(key, value, h)
                self._size += 1
                if first_deletion_index is not None:
                    self._deleted_count -= 1
                break
            if target_slot is _DELETED:
                if first_deletion_index is None:
                    first_deletion_index = target_index
            elif target_slot.h == h and target_slot.key == key:
                target_slot.value = value
                break

            target_index = (target_index + 1) & self._mask

        if self._size > self._resize_threshold:
            self._resize()

    def get(self, key, default=None):
        """Return value for key if present, else default."""
        h = hash(key)
        target_index = h & self._mask

        while True:
            target_slot = self._storage[target_index]
            if target_slot is _EMPTY:
                return default
            if (
                target_slot is not _DELETED
                and target_slot.h == h
                and target_slot.key == key
            ):
                return target_slot.value
            target_index = (target_index + 1) & self._mask

    def delete(self, key: Hashable) -> None:
        h = hash(key)
        target_index = h & self._mask

        while True:
            target_slot = self._storage[target_index]
            if target_slot is _EMPTY:
                raise KeyError(key)
            if (
                target_slot is not _DELETED
                and target_slot.h == h
                and target_slot.key == key
            ):
                self._storage[target_index] = _DELETED
                self._size -= 1
                self._deleted_count += 1
                if self._deleted_count >= self._deleted_clean_ratio * self._capacity:
                    self._rehash_clean()
                return
            target_index = (target_index + 1) & self._mask

    @staticmethod
    def _next_pow2(n: int) -> int:
        cap = 1
        while cap < n:
            cap <<= 1
        return cap

    def _maybe_grow_or_clean(self) -> None:
        """
        Called before inserting new keys to keep probes short.
        Prefer growth when load threshold would be exceeded by one addition;
        otherwise clean if the deleted sentinels are too many.
        """
        if self._size + 1 > self._resize_threshold:
            self._resize()
            return
        if self._deleted_count > int(self._capacity * self._deleted_clean_ratio):
            self._rehash_clean()

    def _rehash_into(self, new_capacity: int) -> None:
        """Rebuild into a fresh table of 'new_capacity', copying only real entries."""
        new_capacity = self._next_pow2(max(8, new_capacity))
        new_table: list[object | _Entry] = [_EMPTY] * new_capacity
        new_mask = new_capacity - 1

        for slot in self._storage:
            if not isinstance(slot, _Entry):
                continue
            idx = slot.h & new_mask
            while new_table[idx] is not _EMPTY:
                idx = (idx + 1) & new_mask
            new_table[idx] = slot

        self._storage = new_table
        self._capacity = new_capacity
        self._mask = new_mask
        self._resize_threshold = int(self._capacity * self._max_load)
        self._deleted_count = 0

    def _resize(self) -> None:
        """Grow (typically 2x) and rehash entries (drops tombstones)."""
        self._rehash_into(self._capacity << 1)

    def _rehash_clean(self) -> None:
        """Keep capacity but drop tombstones by rebuilding."""
        self._rehash_into(self._capacity)

    def __len__(self):
        return self._size

    def __setitem__(self, key: Hashable, value: Any):
        self.insert(key, value)

    def __getitem__(self, key: Hashable):
        v = self.get(key, default=_EMPTY)
        if v is _EMPTY:
            raise KeyError(key)
        return v

    def __contains__(self, key: Hashable):
        return self.get(key, default=_EMPTY) is not _EMPTY
