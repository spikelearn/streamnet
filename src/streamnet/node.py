#Copyright Argonne 2022. See LICENSE.md for details.

class Node:
    """Implement a node from a streamnet
    
    Args:

        n_in : number of inputs taken by the object
        n_out : number of outputs returned by the object
        object : object attached to the node, should be callable, and it may
            return one or more outputs
        default_value : default or starting value of the node
    
    """

    def __init__(self, n_in, n_out, object, default_value):

        self.object = object
        self.n_in = n_in
        if n_out == 1:
            self._out = [default_value]
        else:
            self._out = default_value
        self.n_out = n_out

    def run_object_method(self, name, *args):
        """Executes a method of the object stored in the node

        Args:
            name : name of the method
            args : arguments passed to the object method

        Returns:
            The output of the object method call
        """
        m = getattr(self.object, name)
        return m(*args)
        
    def __call__(self, *args):
        """Calls the object contained in the node

        The output of the last call is stored in the node.

        Args:
            args : argument list passed to the object method
        
        """
        if self.n_out == 1:
            self._out = [self.object(*args)]
        else:
            self._out = self.object(*args)
        return self.out

    @property
    def out(self):
        """
        Retrieves the output of the last call to the object stored
        in the node
        """
        return self._out
    

