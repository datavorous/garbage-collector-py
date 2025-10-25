from ms_gc import MarkSweepGC


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print("=" * 60)


def test_basic_allocation():
    print_section("TEST 1: Basic Allocation")
    gc = MarkSweepGC()

    obj_a = gc.alloc("Node A")
    obj_b = gc.alloc("Node B")
    obj_c = gc.alloc("Node C")
    obj_d = gc.alloc("Node D")

    print("\n1. After allocation (all in young generation):")
    print(gc.heap_snapshot())

    gc.set_field(obj_a, "left", obj_b)
    gc.set_field(obj_a, "right", obj_d)
    gc.set_field(obj_b, "child", obj_c)

    print("\n2. After setting field relationships:")
    print(gc.heap_snapshot())

    gc.add_root(obj_a)
    print("\n3. After adding obj_a as root:")
    print(gc.heap_snapshot())

    gc.gc()
    print("\n4. After first GC (minor) - obj_a, obj_b, obj_c, obj_d survive:")
    print(gc.heap_snapshot())

    gc.set_field(obj_a, "right", None)
    print("\n5. After removing reference to obj_d:")
    print(gc.heap_snapshot())

    gc.gc()
    print("\n6. After second GC - obj_d should be freed, survivors age:")
    print(gc.heap_snapshot())

    gc.gc()
    print("\n7. After third GC - obj_a, obj_b, obj_c promoted to old generation:")
    print(gc.heap_snapshot())


def test_circular_references():
    print_section("TEST 2: Circular References")
    gc = MarkSweepGC()

    node_a = gc.alloc("A")
    node_b = gc.alloc("B")
    node_c = gc.alloc("C")

    gc.add_root(node_a)
    gc.set_field(node_a, "next", node_b)
    gc.set_field(node_b, "next", node_c)
    gc.set_field(node_c, "next", node_a)

    print("\n1. Circular reference A->B->C->A (A is root):")
    print(gc.heap_snapshot())

    orphan_x = gc.alloc("X")
    orphan_y = gc.alloc("Y")
    orphan_z = gc.alloc("Z")
    gc.set_field(orphan_x, "next", orphan_y)
    gc.set_field(orphan_y, "next", orphan_z)
    gc.set_field(orphan_z, "next", orphan_x)

    print("\n2. Added orphan circular reference X->Y->Z->X (no root):")
    print(gc.heap_snapshot())

    gc.gc()
    print("\n3. After GC - orphan cycle collected, rooted cycle survives:")
    print(gc.heap_snapshot())


def test_promotion():
    print_section("TEST 3: Generational Promotion")
    gc = MarkSweepGC()

    persistent = gc.alloc("Persistent")
    gc.add_root(persistent)

    print("\n1. Initial state with one rooted object:")
    print(gc.heap_snapshot())

    for i in range(3):
        gc.gc()
        print(f"\n2.{i+1}. After GC #{i+1}:")
        print(gc.heap_snapshot())
        print(f"     (age increments, promotion happens at age >= 2)")


def test_old_to_young_references():
    print_section("TEST 4: Old->Young References (Card Table)")
    gc = MarkSweepGC()

    old_obj = gc.alloc("Old Object")
    gc.add_root(old_obj)

    # Promote to old generation
    gc.gc()
    gc.gc()

    print("\n1. After promoting object to old generation:")
    print(gc.heap_snapshot())

    young_obj = gc.alloc("Young Object")
    print("\n2. After allocating young object (not connected yet):")
    print(gc.heap_snapshot())

    gc.set_field(old_obj, "ref", young_obj)
    print("\n3. After creating old->young reference (triggers card table):")
    print(gc.heap_snapshot())
    print(f"   Card table: {gc.card_table}")

    gc.minor_gc()
    print("\n4. After minor GC - young object kept alive by old object:")
    print(gc.heap_snapshot())


def test_full_gc_trigger():
    print_section("TEST 5: Full GC Trigger (every 8 minor GCs)")
    gc = MarkSweepGC()

    root = gc.alloc("Root")
    gc.add_root(root)

    print("\n1. Triggering multiple GCs to reach full GC:")
    for i in range(10):
        temp = gc.alloc(f"Temp_{i}")
        gc.gc()
        print(
            f"   GC #{i+1}: minor_gc_count={gc._minor_gc_count}, "
            f"young={len(gc.young)}, old={len(gc.old)}"
        )
        if i == 7:
            print("   ^^^ Full GC triggered (count % 8 == 0)")


def test_root_management():
    print_section("TEST 6: Root Management")
    gc = MarkSweepGC()

    obj_a = gc.alloc("A")
    obj_b = gc.alloc("B")

    gc.add_root(obj_a)
    gc.add_root(obj_b)

    print("\n1. Two objects as roots:")
    print(gc.heap_snapshot())

    gc.gc()
    print("\n2. After GC - both survive:")
    print(gc.heap_snapshot())

    gc.remove_root(obj_b)
    print("\n3. After removing obj_b from roots:")
    print(gc.heap_snapshot())

    gc.gc()
    print("\n4. After GC - obj_b should be collected:")
    print(gc.heap_snapshot())


if __name__ == "__main__":
    print("\n" + "█" * 60)
    print("  GENERATIONAL MARK-AND-SWEEP GC TEST SUITE")
    print("█" * 60)

    test_basic_allocation()
    test_circular_references()
    test_promotion()
    test_old_to_young_references()
    test_full_gc_trigger()
    test_root_management()

    print("\n" + "█" * 60)
    print("  ALL TESTS COMPLETED")
    print("█" * 60 + "\n")
