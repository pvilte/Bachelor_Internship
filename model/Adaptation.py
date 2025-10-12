from model.Node import Node


class Adaptation(Node):
    def __init__(self, adaptation_type, time, change):
        super().__init__("Adaptation")
        self.adaptation_type = adaptation_type
        self.time = time
        self.change = change