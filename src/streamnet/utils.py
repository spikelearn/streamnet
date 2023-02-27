#Copyright Argonne 2022. See LICENSE.md for details.


class DoubleList:

    def __init__(self):
        self.olist = []
        self.odict = {}

    def append(self, obj):
        self.olist.append(obj)
        self.odict[obj] = len(self.olist)-1
    
    def index(self, obj):
        return self.odict[obj]
    
    def contains(self, obj):
        return obj in self.odict
    
    def get(self, ind):
        return self.olist[ind]
    