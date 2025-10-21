# Garbage Collector

## definition

if the program has no way to access a piece of memory anymore, that memory is garbage
so the GC should reclaim it

in low level languages like C/C++, we allocate and free memory manually. if we forget to free memory, we leak it, or free the wrong thing, we crash
the GC automates this, so the programmer doesnt need to track memory lifetime explicitly

programs create tons of temp objs. we only want to keep memory for data that is reachable and still needed

so GC asks two questions:
1. what memory is still in use (reachable)?
2. what can be freed safely (unreachable)?

## history

the very first gc was invented by john mccarthy, the creator of lisp, in around '59-'60.

lisp introduced lists, recursion and dynamic allocation
but programmers had no safe way to free memory of old lists
that were no longer used

so mccarthy proposed a concept: the system itself should detect unused objects and reclaim memory automatically

he published the idea in "Recursive Functions of Symbolic Expressions(1960)" -> led to mark and sweep algorithm.

early research on GC gave

1959-60 : mark and sweep -> trace reachable objects, and delete others
early 60s : reference counting (colling et al) -> keep a reference counter on each object

late 60s : copying gc (cheney, 1970) -> copy live data into a fresh space, compacting it

## example

```py
function loadPeople():
	tempList = [] # temporary list created
	for name in ["A", "B", "C"]:
		p = new Person(name) # allocated
		> alter:
			p = malloc(Person)
			p.name = name

		tempList.append(p)

	result = process(tempList)
	> alter:
		free(tempList)
	return result # tempList will die here

function process(list):
	alive = []
	> alter:
		alive = malloc(List)
	for person in list:
		if person.name != "B":
			alive.append(person)
		> alter:
			else:
				free(person)
	return alive

function main():
	finalList = loadPeople()
	print(finalList) # prints A, C
	# after this line, finalList dies too
	# GC automatically frees A, C and everything else
	> alter:
		for person in finalList:
			free(person)
		free(finalList)
```
if we miss even one fee --> memory leak
if freed too early -> dangling pointer / crash
if you double free -> head corruption

# how things might have started...

when we build lists and trees at runtime, when functions recursively construct new structures, you naturally produce huge amounts of temporary data that outlives its usefulness very quickly
symbolic computation generates garbage by design

humans are terrible at tracking dynamic memory lifetimes
but the machine already knows tall active references, so why not make it do the bookkeeping


Lisp data structures are graphs, in GT:
> NODES reachable from the root are part of the structure, everything else is irrelevant

this translates into memory:
roots = stack, gloval, registers (always usable references)
reachable objects = memory we must keep
unreachable objects = now just garbage

1. mark all reachable nodes by tracing pointers
2. sweep everything unmarked

# Topics for Phase 1

## object/heap allocation

an object is a chunk of memory you allocate on the heap to store data (like a struct or a small record with fields)

GC manages heap objects, we need a clear idea of what an "allocated object" is, and where it lives.

## reference/pointer

a reference or pointer is a link from one object to another, or from a root variable to an object

reference counting is literally about counting references, if we can't track references, we cant free memory safely

## root set

the root set is the set of variables that are directly accessible from the program (global vars, stack vars, or manually tracked roots)

an obj with no path from any root is garage, we need the concept of roots to know when an object is still in use

## reference count

each object stores a small integer refcount that tracks how many references point to it
RC works by:
	refcount++ when a new ref is added
	refcount-- when a new ref goes away

## freeing or reclaiming memory

freeming mem means remocing and object from the heap and releasing its storage
reference counting must destroy objects with refcount==0

## obj graph

all heap objs plus their refs form a graph
(nodes = objs, edges = pointers)

RC fails on cyclic graphs

a cycle happens when A references B and B references A.
even if no root points to them, their refcounts never drop to zero

this will be the cause for us to move on to phase 2, but that's a differnt chapter.

here is what we will work on:

- [ ] implement rc_gc.py -> reference counting collector
- [ ] add smoke tests for rc_gc
- [ ] show cycle leak in rc_gc example

so essentially:
we want this from the phase 1 of RC toy GC:

a GC object that owns a heap and a root set
alloc() to make objects
incref() / decref() semantics
a way to inspect the heap

obj - node on the heap. has identity, option value, fields (named pointers), refcount, and a freed flag

heap - mapping ID -> object, owned by the GC instance

root set - the set of references the program holds (variable). if no path from any root reaches an object, it's garbage

reachable - an object is reachable if there exists a path of references from any root to that object

reference counting (RC) each object tracks how many incoming referneces it has (a small integer)
when it hits 0 we free it (and recursively adjust children)

```python
gc = ReferenceCountingGC()

HEAP = empty {}
ROOT = empty set()

ref_a = gc.alloc("Alice")
> alloc() generates a new ID (1)
> creates _Obj(id=1, value="Alice", refcount=0, fields={})
> Stores in heap: heap[1] = _Obj()#1
> returns  ObjectRef pointing to it

HEAP = {1: _Obj() (val="Alice", rc=0) #1
ROOTS = {}

ref_a --> _Obj#1 -> refcount: 0 (not protected yet)

gc.add_root(ref_a)
> Adds '1' to 'roots' set
> calls incref(ref_a) -> _Obj #1.refcount +=1

HEAP: {1: _Obj} #1 (val='Alice', rc=1)
ROOTS: {1}
ref_a -> _Obj #1 refcount: 1 (protected)

similarly,
ref_b = gc.alloc("Bob")
gc.set_field(ref_a, "friend", ref_b)
> new child gets incremented
> link is created

parent.fields["friend"] = ref_b

HEAP: {
	1: _Obj #1 (val="Alice", rc=1, fields={friend -> #2}),
	2: _Obj #2 (val='Bob', rc=1)
}
ROOTS: {1}
ref_a -> _Obj #1 -- friend --> _Obj #2 <-ref_b>
		rc = 1					rc = 1
```
# mark and sweep




