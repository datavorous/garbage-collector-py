from ms_gc import MarkSweepGC

gc = MarkSweepGC()
"""
obj_a = gc.alloc("Node A")
obj_b = gc.alloc("Node B")
obj_c = gc.alloc("Node C")
obj_d = gc.alloc("Node D")

print(gc.heap_snapshot())


gc.set_field(obj_a, "left", obj_b)
gc.set_field(obj_a, "right", obj_d)
gc.set_field(obj_b, "child", obj_c)

print(gc.heap_snapshot())

gc.add_root(obj_a)
print(gc.heap_snapshot())

gc.gc()
print(gc.heap_snapshot())


gc.set_field(obj_a, "right", None)
print(gc.heap_snapshot())

gc.gc()
print(gc.heap_snapshot())
"""
node_a = gc.alloc("A")
node_b = gc.alloc("B")
node_c = gc.alloc("C")
gc.add_root(node_a)
gc.set_field(node_a, "next", node_b)
gc.set_field(node_b, "next", node_c)
gc.set_field(node_c, "next", node_a)
print(gc.heap_snapshot())

orphan_x = gc.alloc("X")
orphan_y = gc.alloc("Y")
orphan_z = gc.alloc("Z")

gc.set_field(orphan_x, "next", orphan_y)
gc.set_field(orphan_y, "next", orphan_z)
gc.set_field(orphan_z, "next", orphan_x)
print(gc.heap_snapshot())

gc.gc()
print(gc.heap_snapshot())
