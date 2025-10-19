from model.Node import Node

class Process(Node):
    """
    This class describes a Process - a definition of a workflow/choreography. The superclass is Node because
    Process is a node in the database.

    :param id_proc(string): the ID of the process
    """

    def __init__(self, id_proc):
        super().__init__("Process")
        self.id_proc = id_proc