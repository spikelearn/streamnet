#Copyright Argonne 2022. See LICENSE.md for details.

"""

An node has the following interface:

- It needs to be callable
- It has to implement out, which stores the result of the last
  computation, either as a single output or a list of outputs

"""

class StreamNet:

    """
    Implement a streamnet

    Args:
        return_values: bool, streamnet returns value after call


    """

    def __init__(self, return_values=True):

        self._iports = []
        self._iports_dict = {}
        self._oports = []
        self._nodes = {}
        self._el_name_dict = {}
        self._el_in = {}
        self._el_out = {}
        self.return_values = return_values


    def add_node(self, name, el, n_in=0, n_out=1):
        """Adds an node to the streamnet

        Args:
            name : the name of the node
            el : an node
            n_in : number of inputs
            n_out : number of outputs
        
        Raises:
            ValueError: User tries to reuse an existing name
        """

        if name in self._nodes.keys():
            raise ValueError("node {} already defined".format(name))

        self._nodes[name] = el
        self._el_in[name] = [None for i in range(n_in)]
        self._el_out[name] = n_out

    def get_node_names(self):
        return self._nodes.keys()[:]

    def get_input_names(self):
        return self._iports[:]

    def add_input(self, name):
        """Adds an external input
        
        Args:
            name: the name of the input

        Raises:
            ValueError: User tries to reuse an existing name
        """

        if name in self._iports:
            raise ValueError("Input {} already defined".format(name))
        self._iports.append(name)
        self._iports_dict[name] = len(self._iports)-1

    def add_output(self, name, n=1):
        """Defines an output
        
        Args:
            name: name of the layer
            n: index of the node output to be returned (optional, default 1)
             
        """
        if name in self._nodes.keys():
            if self._el_out[name] > n:
                raise ValueError("node {} has fewer than {} outputs".format(name, n))
            else:
                self._oports.append((name, n))
        elif name in self._iports:
            self._oports.append((name,))
        else:
            raise ValueError("node or Input {} not found".format(name))

    def set_el_inputs(self, name, *args):
        if name not in self._nodes.keys():
            raise ValueError("node or Input {} not found".format(name))
        arg_list = []
        for arg in args:
            if isinstance(arg, str):
                if not self.name_exists(arg):
                    raise ValueError("node or Input {} not found".format(arg))
                arg_list.append((arg,))
            else:
                if arg[0] not in self._nodes.keys():
                    raise ValueError("node {} not found".format(arg[0]))
                arg_list.append(arg)
        self._el_in[name] = arg_list

    def set_el_input(self, el_name, n_in, name, n_out=None):
        if name not in self._nodes.keys():
            raise ValueError("node or Input {} not found".format(name))

        if n_out is None:
            self._el_in[el_name][n_in] = (name,)
        else:
            self._el_in[el_name][n_in] = (name, n_out)

    def name_exists(self, name):
        return (name in self._nodes.keys()) or (name in self._iports)
    
    def add_el_input(self, el_name, name, n_out=None):
    
        if not self.name_exists(name):
            raise ValueError("node or Input {} not found".format(name))

        if n_out is None:
            self._el_in[el_name].append((name,))
        else:
            self._el_in[el_name].append((name, n_out))

    def broadcast(self, method_name, *method_args):
        for _, el in self._nodes.items():
            f = getattr(el, method_name)
            f(*method_args)

    def __call__(self, *args):
        input_dict = {}
        for name, el in self._nodes.items():
            input_list = []
            for el_input in self._el_in[name]:
                inp_name = el_input[0]
                if inp_name in self._iports:
                    input_list.append(args[self._iports_dict[inp_name]])
                else:
                    if len(el_input) == 1:
                        n_out = 1
                    else:
                        n_out = el_input[1]

                    if self._el_out[inp_name] == 1:
                        if n_out == 1:
                            input_list.append(self._nodes[inp_name].out)
                        else:
                            raise ValueError("{} is greater than the number of outputs".format(n_out))
                    else:
                        input_list.append(self._nodes[inp_name].out[n_out])
            input_dict[name] = input_list
        
        for name, el in self._nodes.items():
            el(*input_dict[name])
        
        self.out = []

        for op in self._oports:
            if len(op) == 1:
                self.out.append(args[self._iports_dict[op[0]]])
            else:
                name, nout = op
                if self._el_out[name] == 1:
                    self.out.append(self._nodes[name].out)
                else:
                    self.out.append(self._nodes[name].out[nout-1])
        
        if self.return_values:
            return self.out

