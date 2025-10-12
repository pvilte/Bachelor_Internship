from model.Node import Node


class Initiator(Node):
    def __init__(self, name, id_number):
        super().__init__("Initiator")
        self.name = name
        self.id_number = id_number