from model.Node import Node


class Initiator(Node):
    def __init__(self, name):
        super().__init__("Initiator")
        self.name = name