from model.Node import Node


class Event(Node):
    def __init__(self, name, time, resource):
        super().__init__("Event")
        self.name = name
        self.time = time
        self.resource = resource
