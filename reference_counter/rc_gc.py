from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Set
import itertools


@dataclass
class _Obj:
    id: int
    value: Any = None
    fields: Dict[str, "ObjectRef"] = field(default_factory=dict)
    refcount: int = 0
    freed: bool = False

    def __repr__(self):
        flds = [f"{k} -> #{v._obj.id}" for k,v in self.fields.items()]
        return f"_Obj #{self.id} (val={self.value!r}, rc={self.refcount}), fields={flds}, freed={self.freed}"


class ObjectRef:
    def __init__(self, _obj: _Obj):
        self._obj = _obj

    def __repr__(self):
        return f"ObjectRef(#{self._obj.id}), val={self._obj.value!r}"


class ReferenceCountingGC:
    def __init__(self):
        # created an infinite couter (1..infinity)
        # each call to next() returns 1,2,3... and so on
        self._next_id = itertools.count(1)

        # simulated version of memory/heap, values will be the _Obj instance
        self.heap: Dict[int, _Obj] = {}

        # "root" objects, these are protected from garbage collection
        self.roots: Set[int] = set()


    def alloc(self, value: Optional[Any] = None) -> ObjectRef:
        # get new counter id, build new instance, push to heap
        oid = next(self._next_id)
        obj = _Obj(
                id=oid,
                value=value,
                refcount=0, # nobody references it yet, so sad :(
                fields={}, # neither is it referenced by other objects
                freed=False # it means the object is alive
            )
        self.heap[oid] = obj

        return ObjectRef(obj)


    def _get_obj(self, obj_ref: Optional[ObjectRef]) -> Optional[_Obj]:
        if obj_ref is None:
            return None
        return obj_ref._obj


    def incref(self, obj_ref: Optional[ObjectRef]) -> None:
        obj = self._get_obj(obj_ref)
        if obj is None or obj.freed:
            return
        obj.refcount += 1


    def decref(self, obj_ref: Optional[ObjectRef]) -> None:
        obj = self._get_obj(obj_ref)
        if obj is None or obj.freed:
            return
        obj.refcount -= 1
        if obj.refcount <= 0:
            self._free(obj)


    def _free(self, obj: _Obj) -> None:
        # helps to deallocate an object from memory
        # the CORE of the garbage collection program

        if obj.freed:
            # this helps to guard against double free, and prevent infinte recursion
            return
        obj.freed = True
        # this prevents circular recursions

        children = list(obj.fields.values())
        # extracing all the objectRefs that this obj points to
        # and create a copy, because we are about to clear the dict below
        # and now the obj is an disconnected fully
        obj.fields.clear()

        # cascade chain rxn starts heere
        # A->B->C freeing A will decrement B, potentially freeing B, which drecrements C...
        for child_ref in children:
            self.decref(child_ref)


        if obj.id in self.heap:
            # we remove the object from memory, it's gone for ever.
            # fly me to the moon
            # and let me play among the stars
            # and let me see what spring is like
            # on a jupiter and mars
            del self.heap[obj.id]

    def set_field(self, parent_ref: ObjectRef, field_name: str, new_child_ref: Optional[ObjectRef]) -> None:
        # set a field on a parent obj to point to a child obj
        parent = self._get_obj(parent_ref)
        if parent is None or parent.freed:
            # print("Setting field on freed or non existent parent")
            raise RuntimeError("Setting field on freed or non existent parent.")

        old_child_ref = parent.fields.get(field_name)
        if old_child_ref is new_child_ref:
            return
        if new_child_ref is not None:
            self.incref(new_child_ref)


        if new_child_ref is None:
            if field_name in parent.fields:
                del parent.fields[field_name]
        else:
            parent.fields[field_name] = new_child_ref

        if old_child_ref is not None:
            self.decref(old_child_ref)


    def add_root(self, obj_ref: ObjectRef) -> None:
        obj = self._get_obj(obj_ref)
        if obj is None or obj.freed:
            return

        if obj.id in self.roots:
            return

        self.roots.add(obj.id)
        self.incref(obj_ref)


    def remove_root(self, obj_ref: ObjectRef) -> None:
        obj = self._get_obj(obj_ref)
        if obj is None or obj.freed:
            return
        if obj.id not in self.roots:
            return

        self.roots.remove(obj.id)
        self.decref(obj_ref)


    def heap_snapshot(self) -> str:
        lines = [f"HEAP size={len(self.heap)}, ROOTS={sorted(list(self.roots))}"]
        for oid in sorted(self.heap):
            lines.append(repr(self.heap[oid]))
        return "\n".join(lines)

