from model.Node import Node


class Process(Node):
    def __init__(self, id_proc):
        super().__init__("Process")
        self.id_proc = id_proc