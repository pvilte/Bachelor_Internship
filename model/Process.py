from model.Node import Node


class Process(Node):
    def __init__(self, id_number, name):
        super().__init__("Process")
        self.id_number = id_number
        self.name = name