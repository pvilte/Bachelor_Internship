from model.Node import Node

"""
This class describes Adaptation - a change that can be applied to an event. Adaptation is a node
in the database, the superclass is Node.

Attributes:
    + adaptation_type(string) - type of adaptation (usually "insert", "delete"; possible to assign other values)
    + time(datetime) - time when the adaptation was applied to an event
    + change(string) - what exactly was changed
"""

class Adaptation(Node):
    def __init__(self, adaptation_type, time, change):
        super().__init__("Adaptation")
        self.adaptation_type = adaptation_type
        self.time = time
        self.change = change