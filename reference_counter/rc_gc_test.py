from rc_gc import ReferenceCountingGC

'''
gc = ReferenceCountingGC()
a = gc.alloc("A")
b = gc.alloc("B")
print("after allocations (refcount=0 until we add roots): ")
print(gc.heap_snapshot())
'''

def test_acyclic():
    print("acyclic chain: should be reclaimed when root removed")
    gc = ReferenceCountingGC()
    root = gc.alloc("root-holder")
    gc.add_root(root)
    a = gc.alloc("A")
    b = gc.alloc("B")
    gc.set_field(root, "child", a)
    gc.set_field(a, "child", b)

    print("Before removing root:")
    print(gc.heap_snapshot())
    gc.remove_root(root)
    print(gc.heap_snapshot())
    print("-" * 60)

test_acyclic()


def smoke_test_cycle():
    print("SMOKE: cycle demo -> RC should NOT collect the cycle automatically")
    gc = ReferenceCountingGC()
    a = gc.alloc("A")
    b = gc.alloc("B")
    gc.set_field(a, "peer", b)
    gc.set_field(b, "peer", a)

    gc.add_root(a)
    gc.add_root(b)
    print("Before removing roots (while roots exist):")
    print(gc.heap_snapshot())
    gc.remove_root(a)
    gc.remove_root(b)
    print("After removing roots (expected: cycle remains in heap):")
    print(gc.heap_snapshot())

    # manual break (for demonstration) to reclaim:
    print("Manually breaking the cycle and clearing fields:")
    # only clear if not freed (safety)
    if a._obj.id in gc.heap and not a._obj.freed:
        gc.set_field(a, "peer", None)
    if b._obj.id in gc.heap and not b._obj.freed:
        gc.set_field(b, "peer", None)
    print("After manual break (expected: objects reclaimed):")
    print(gc.heap_snapshot())
    print("-" * 60)

smoke_test_cycle()
