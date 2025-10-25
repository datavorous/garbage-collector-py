from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Set
import itertools


@dataclass
class _Obj:
    id: int
    value: Any = None
    # REM: fields has a type hint; a dict mapping str -> "ObjectRef"
    # the objectref is quoted because its is defined later in the  file < forward ref >
    # the alt method might be to use annotation with __future__ [TODO]

    # field(default_factory=dict) ensures that EACH _Obj GETS ITS OWN DICT
    # using = {} would have shared across all instances
    fields: Dict[str, "ObjectRef"] = field(default_factory=dict)
    marked: bool = False
    freed: bool = False

    def __repr__(self):

        if self.fields:
            flds = [f"{k} -> #{v._obj.id}" for k, v in self.fields.items()]
            fstr = "[" + ", ".join(flds) + "]"
        else:
            fstr = "[]"

        return f"_Obj #{self.id} (val={self.value!r}, marked={self.marked}, freed={self.freed}, fields={fstr})"
        # flds = [f"{k} -> #{v._obj.id}" for k, v in self.fields.items()]
        # return f"_Obj #{self.id} (val={self.value!r}, marked={self.marked})"


class ObjectRef:
    # techincally a wrapper class, with a repr
    def __init__(self, _obj: _Obj):
        self._obj = _obj

    def __repr__(self):
        # NEW: !r calls repr() instead of str()
        return f"ObjectRef(#{self._obj.id}), val={self._obj.value!r}"


class MarkSweepGC:
    def __init__(self):
        self._next_id = itertools.count(1)
        self.heap: Dict[int, _Obj] = {}
        self.roots: Set[int] = set()

    def alloc(self, value: Optional[Any] = None) -> ObjectRef:
        # we increment the counter
        # build an obj, and put it in our heap
        # we wrap the obj ins a objref, and return back
        oid = next(self._next_id)
        obj = _Obj(id=oid, value=value)
        self.heap[oid] = obj
        return ObjectRef(obj)

    def _get_obj(self, obj_ref: Optional[ObjectRef]) -> Optional[_Obj]:
        if obj_ref is None:
            return None
        return obj_ref._obj

    def set_field(
        self, parent_ref: ObjectRef, field_name: str, child_ref: Optional[ObjectRef]
    ) -> None:
        parent = self._get_obj(parent_ref)
        if parent is None or parent.freed:
            raise RuntimeError("setting field on freed or non existent parent.")

        if child_ref is None:
            if field_name in parent.fields:
                del parent.fields[field_name]
        else:
            parent.fields[field_name] = child_ref

    def add_root(self, obj_ref: ObjectRef) -> None:
        obj = self._get_obj(obj_ref)
        if obj is None or obj.freed:
            return
        if obj.id in self.roots:
            return
        self.roots.add(obj.id)

    def remove_root(self, obj_ref: ObjectRef) -> None:
        obj = self._get_obj(obj_ref)
        if obj is None or obj.freed:
            return
        self.roots.discard(obj.id)

    def _mark(self, obj: Optional[_Obj]) -> None:
        if obj is None or obj.freed:
            return

        if obj.marked:
            return

        obj.marked = True
        for child_ref in obj.fields.values():
            child = self._get_obj(child_ref)
            self._mark(child)

    def _sweep(self) -> None:
        to_free = []

        for oid, obj in list(self.heap.items()):
            if obj.marked:
                obj.marked = False
            else:
                to_free.append(oid)

        for oid in to_free:
            self._free(oid)

    def _free(self, oid: int) -> None:
        obj = self.heap.get(oid)
        if obj is None:
            return
        if obj.freed:
            return

        obj.freed = True
        obj.fields.clear()
        del self.heap[oid]

    def gc(self) -> None:
        for root_id in list(self.roots):
            obj = self.heap.get(root_id)

            if obj is not None:
                self._mark(obj)

        self._sweep()

    def heap_snapshot(self) -> str:
        lines = [f"HEAP size={len(self.heap)}, ROOTS={sorted(list(self.roots))}"]
        for oid in sorted(self.heap):
            lines.append(repr(self.heap[oid]))
        return "\n".join(lines)
