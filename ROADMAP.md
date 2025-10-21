# garbage collector from scratch (python)

## phase 1 -> setup
- [x] initialize repo and directory layout
- [x] add basic readme and license
- [x] implement rc_gc.py -> reference counting collector
- [x] add smoke tests for rc_gc
- [x] show cycle leak in rc_gc example

## phase 2 -> mark and sweep
- [x] create ms_gc.py -> mark and sweep collector
- [x] implement root tracking -> add_root/remove_root
- [ ] add manual collect() method
- [x] test with acyclic and cyclic graphs
- [x] confirm unreachable cycles reclaimed

## phase 3 -> core api stabilization
- [ ] define uniform interface -> alloc, set_field, add_root, remove_root, collect
- [ ] add statistics -> allocated, freed, collected, heap_size
- [ ] add context manager -> root_scope
- [ ] create small benchmark/timing harness

## phase 4 -> extensions
- [ ] implement tracer api -> object.trace(visitor)
- [ ] refactor rc and ms to use tracer
- [ ] add semi-space copying collector -> young generation
- [ ] implement generational scheme -> young/old separation
- [ ] add promotion policy -> survive N collections -> promote
- [ ] implement compaction -> forwarding pointers
- [ ] add write barrier -> old to young references

## phase 5 -> advanced exploration
- [ ] simulate incremental marking -> tri-color abstraction
- [ ] experiment with concurrent mark phase -> threaded mock
- [ ] measure gc pause times
- [ ] visualize heap graphs -> graphviz
- [ ] compare throughput -> rc vs ms vs generational

## phase 6 -> documentation and validation
- [ ] write design doc -> object model, roots, edges
- [ ] add diagrams -> mark-sweep, generational flow
- [ ] document limitations -> python memory not reclaimed
- [ ] summarize trade-offs -> rc, ms, copying, generational
- [ ] finalize readme -> usage + references
