"""
This class describes Node - a superclass of all classes in the model package.
Labels are given in such way that each node can have only one label because of the context of the project.

Attributes:
    - label - the label of a node
"""

class Node:
    def __init__(self, label):
        self.__label = label
