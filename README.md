# streamnet
A directed netlist representation for stream processing

## What is a streamnet object?

A streamnet object (for lack of an existing term) is essentially a directed graph
composed of a set of nodes with a predefined number of input and output ports and
a input/output interface to connect with the external world.

- Nodes have numbered input and output ports. They can be zero, in which case
  they become internal sources or sinks.
- Each node contains an object that is callable, taking a number of inputs
  equal to the number of input ports of a node and producing a number of
  outputs equal to the number of output ports.
- Inputs and output ports provide an interface with the external world

These nodes are connected by directed edges with the following restriction:

- Input ports in each node must have an indegree of one
- There are no restrictions in the outdegree of output pins, including zero


### What does this streamnet represent?

Streamnets represent a subset of circuits and architectures where information or causality flows between components in a directional way.

### What is the execution model of this network?

The execution model is essentially a flavor of dataflow programming:

A call to a streamnet object leads to a synchronous execution of all the
nodes, with the inputs automatically pulled based on the network's connectivity.

In addition to calls, the streamnet can broadcast instructions that lead to
the executing of methods defined in the objects attached to the nodes. In
order for broadcasting to work, all nodes must have objects with consistent
interfaces.

## Wait, is this a new type of object?

There are many dataflow or flow programming languages that probably implement similar abstractions.
Streamnet is a variation on netlists in the sense that it is directed and input pins must have
an indegree of one. It is also a generalization of flow networks and similar
to how programming languages like Labview operate.

The purpose here is that they can encapsulate arbitrary computations.

## Streamnet implementaation

This repository contains a Python implementation of a Streamnet. 
Longer term goals is to recreate this model in a way that takes advantage of parallelism.

## Team

Streamnet is being developed by Angel Yanguas-Gil as part of Threadwork, a project
funded through DOE.


