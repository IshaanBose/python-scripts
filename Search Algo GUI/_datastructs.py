"""
Contains custom data structures.
"""

class Node:
    """
    This class is used to create tangible nodes for the A* algo to work on.
    """
    def __init__(self, pos, parent=None, g=0, h=0):
        self.pos = pos
        self.parent = parent
        self.g = g
        self.h = h
        self.f = self.g + self.h
        
class AugList(list):
    """
    Behaves like a list with an added functionality used to find Nodes in it.
    """
    def __init__(self, l):
        list.__init__(self, l)
        
    def inlist(self, node):
        for i in range(len(self)):
            if self[i].pos == node.pos:
                return [True, i]
        return [False, None]