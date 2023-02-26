# streamnet
A directed netlist representation for stream processing

## What is a streamnet object?

A streamnet object (for lack of an existing term) is essentially a directed graph
composed of a set of elements, a set of external input ports, a set of
external output ports where:

- Elements are nodes with labeled input and output pins. They can be zero, in which case
  they become internal sources or sinks of information.
- External input ports are nodes with an indegree of zero
- External output ports are nodes with an outdegree of zero

These nodes are connected by directed edges with the following restriction:

- Input pins in each element must have an indegree of one
- There are no restrictions in the outdegree of output pins, including zero

Note that every streamnet object is also an element.

### What does this streamnet represent?

Streamnets represent a subset of circuits and architectures where information flows between components in a directional, causal way. 

### What is the execution model of this network?

The execution model is essentially a flavor of dataflow programming:

A streamnet object has a method `step` that puts new inputs into the input ports
of the network. The `step` instruction
is broadcasted to all elements in the network.

Each element is either its own Streamnet object or an
arbitrary object with a similar interface. Elements can be stateful and/or have side effects outside the streamnet, such as logging.

When a `step` instruction is broadcasted inside a streamnet, all elements pulls the existing input 
states and carry out the computation. This is consistent with a synchronous
execution model, though elements can implement delays and queues. They can also pass information
probabilistically to incorporate asynchronous behavior.

## Wait, is this a new type of object?

There are many dataflow or flow programming languages that probably implement similar abstractions.
Streamnet is a variation on netlists in the sense that it is directed and input pins must have
an indegree of one. It is also a generalization of flow networks.

The purpose here is to serve as a unifying model to tie in circuits, digital architectures, and 
spiking neural networks.

## Streamnet implementaation

This repository contains a Python implementation of a Streamnet. Obviously the goal is to recreate
this model in a way that takes advantage of parallelism.

## Team

Streamnet is being developed by Angel Yanguas-Gil as part of Threadwork, a project
funded through DOE.


