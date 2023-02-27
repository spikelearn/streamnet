#Copyright Argonne 2022. See LICENSE.md for details.

"""

An node has the following interface:

- It needs to be callable
- It has to implement out, which stores the result of the last
  computation, either as a single output or a list of outputs

"""

from .node import Node
from .utils import DoubleList
from collections import namedtuple

Conn = namedtuple("Conn", ["name", "port"], defaults=[None, None])

class StreamNet:

    """
    Implement a streamnet

    Args:
        return_values: bool, streamnet returns value after call


    """

    def __init__(self, return_values=True):

        self._nodes = {}
        self._node_inputs = {}
        self._node_outputs = {}

        self._oports = []
        self.inputs = DoubleList()

        self.return_values = return_values

    def from_dict(self, net_dict, object_dict, default_dict):
        """Generate a streamnet from dictionary objects
        
        Args:
            net_dict: dictionary with the network and connectivity
            object_dict : dictionary with the objects associated with
                each node.
            default_dict : dictionary with the default values for each
                node
        """
        for input_name in net_dict["inputs"]:
            self.add_input(input_name)
        for node in net_dict["nodes"]:
            node_name = node["name"]
            n_in = node["n_in"]
            n_out = node["n_out"]
            self.create_node(node_name, n_in, n_out, 
                object_dict[node_name], default_dict[node_name])
        for con in net_dict["connections"]:
            args = con["to"][:]
            args.extend(con["from"])
            self.set_node_input(*args)
        for output in net_dict["outputs"]:
            self.add_output(*output)


    def add_node(self, name, node):
        """Adds an node to the streamnet

        Args:
            name : the name of the new node
            node : a Node object

        Raises:
            ValueError: User tries to reuse an existing name
        """

        if name in self._nodes.keys():
            raise ValueError("node {} already defined".format(name))

        self._nodes[name] = node
        self._node_inputs[name] = [None for i in range(node.n_in)]
        self._node_outputs[name] = node.n_out


    def create_node(self, name, n_in, n_out, object, default_value):
        """Creates a new node in the streamnet
        
        Args:
            name: the name of the new node
            object: an object, must be callable
            n_in: number of inputs to the object call method
            n_out: number of outputs returned by the object

        """

        node = Node(n_in, n_out, object, default_value)
        self.add_node(name, node)


    def add_input(self, name, to_node=None, to_port=None):
        """Adds an external input, optionally connecting it to an
        input port in an existing node.
        
        Args:
            name: the name of the input
            to_node : name of the node connecting to the input
            to_port : number of othe port connecting to the input

        Raises:
            ValueError: User tries to reuse an existing name
        """
        
        if self.inputs.contains(name):
            raise ValueError("Input {} already defined".format(name))

        self.inputs.append(name)


    def add_output(self, name, n=1):
        """Defines an output
        
        Args:
            name: name of the layer
            n: index of the node output to be returned (optional, default 1)
             
        """
        if self.node_exists(name):
            if self._node_outputs[name] > n:
                raise ValueError("node {} has fewer than {} outputs".format(name, n))
            else:
                self._oports.append(Conn(name, n-1))
        elif self.input_exists(name):
            self._oports.append(Conn(name))
        else:
            raise ValueError("node or Input {} not found".format(name))

    @property
    def node(self, node_name):
        return self._nodes[node_name]


    def __call__(self, *args):
        """Runs the streamnet a single timestep

        Args:
            args : list of inputs, should be equal to the number of input ports

        Returns:

        """

        input_dict = {}
        for node_name, node in self._nodes.items():
            print(node_name)
            input_list = []
            for from_node in self._node_inputs[node_name]:
                print(node_name, from_node)
                from_name = from_node.name
                if from_node.port is None:
                    if self.input_exists(from_name):
                        input_list.append(args[self.inputs.index(from_name)])
                    else:
                        raise ValueError("Input {} not found".format(from_name))

                else:
                    input_list.append(self._nodes[from_name].out[from_node.port])

            input_dict[node_name] = input_list
        
        for name, el in self._nodes.items():
            el(*input_dict[name])
        
        self.out = []

        for op in self._oports:
            if op.port is None:
                self.out.append(args[self.inputs.index(op.name)])

            else:
                self.out.append(self._nodes[op.name].out[op.port])
        
        if self.return_values:
            return self.out


    def set_node_input(self, node_name, node_port, from_name, from_port=None):
        """Sets the input connectivity of a input port of a node
        
        Args:

            node_name : Name of the node
            node_port : Input port number of the node
            from_name : Name of the node or input connecting to the port
            from_port : Output port number if input comes from a node
        """

        if not self.node_exists(node_name):
            raise ValueError("Node {} not found".format(node_name))
        
        if from_port is None:
            if not self.input_exists(from_name):
                raise ValueError("Input {} not found".format(from_name))
            c = Conn(from_name)
        else:
            if not self.node_exists(from_name):
                raise ValueError("Node {} not found".format(from_name))

            c = Conn(from_name, from_port-1)

        self._node_inputs[node_name][node_port-1] = c


    def add_node_input(self, node_name, from_name, from_port=None):
        """Adds and assigns an input port to a node
        
        Args:

            node_name : Name of the node
            from_name : Name of the node or input connecting to the port
            from_port : Output port number if input comes from a node
        """

        if not self.node_exists(node_name):
            raise ValueError("Node {} not found".format(node_name))
        
        
        if from_port is None:
            if not self.input_exists(from_name):
                raise ValueError("Input {} not found".format(from_name))
            c = Conn(from_name)
        else:
            if not self.node_exists(from_name):
                raise ValueError("Node {} not found".format(from_name))

            c = Conn(from_name, from_port-1)

        self._node_inputs[node_name].append(c)
        self.node[node_name].n_in += 1


    def set_node_inputs(self, node_name, conn_list):
        if node_name not in self._nodes.keys():
            raise ValueError("node or Input {} not found".format(node_name))
        if len(conn_list) != self._node_outputs[node_name]:
            raise ValueError("Number of inputs is different from number of ports")
        for i, conn in enumerate(conn_list):
            self.set_node_input(node_name, i+1, *conn)


    def node_exists(self, name):
        return name in self._nodes.keys()
    
    def input_exists(self, name):
        return self.inputs.contains(name)

    def name_exists(self, name):
        return self.node_exists(name) or self.input_exists(name)
    

    def broadcast(self, method_name, *method_args):
        for _, el in self._nodes.items():
            f = getattr(el.object, method_name)
            f(*method_args)

    def get_node_names(self):
        return self._nodes.keys()[:]

    def get_input_names(self):
        return self.inputs.olist[:]
