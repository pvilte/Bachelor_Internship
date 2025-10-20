from model.Node import Node

class Instance(Node):
    """
    This class describes Instance - one run of a Process. Therefore, the instance has a process.
    The superclass is Node.

    :param instance_id: the ID of the instance
    :param process: the process object associated with the instance
    """

    def __init__(self, instance_id, process):
        super().__init__("Instance")
        self.instance_id = instance_id
        self.process = process

