# some-set-partitionner
A bunch of classes in Python to compute a ~~"Venn diagramm"~~ some kind of partitionning

## Usage

Just look at the main function and run it, it's probably easier to understand it this way

## How it works

I use the name "Set" in the code, but unicity isn't really checked
Consider them List that should not have duplicates :^)

The input collections are the `IdentifiedSet`, which are just a list with an identifier

The main machine is the `VennPartitioner` that you instantiate, and call the `add_set` method with a `IdentifiedSet`

The `VennPartitioner`'s `partitions` member is a list of list of `VennPartition`s
This represents "layers" of partitions in the sense that:
- Layer 0 contains the VennPartitions that each have the exclusive elements of one `IdentifiedSet`
- Layer i ( for i > 0 ) contains the VennPartitions that each have the intersection ( in the sense of Set theory ) of i + 1 `IdentifiedSet`
