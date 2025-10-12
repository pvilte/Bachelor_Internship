from model.Node import Node


class Instance(Node):
    def __init__(self, instance_id):
        super().__init__("Instance")
        self.instance_id = instance_id

