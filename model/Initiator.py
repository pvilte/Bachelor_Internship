from model.Node import Node

class Initiator(Node):
    """
    This class describes Initiator - the participant who invoked an adaptation. The superclass is Node, Initiator
    is a node in the database.

    Attributes:
        name(string) - the name of the Initiator
    """

    def __init__(self, name):
        super().__init__("Initiator")
        self.name = name