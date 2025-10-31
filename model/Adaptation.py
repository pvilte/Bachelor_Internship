from model.Node import Node

class Adaptation(Node):
    """
    This class describes Adaptation - a change that can be applied to an event. Adaptation is a node
    in the database, the superclass is Node.

    :param adaptation_id: the ID of the adaptation
    :param adaptation_type: type of adaptation (usually "insert", "delete"; possible to assign other values)
    :param time(datetime): time when the adaptation was applied to an event
    :param change(string): what exactly was changed
    :param initiator(string): who initiated this change
    """

    def __init__(self, adaptation_id, adaptation_type, time, change, initiator):
        super().__init__("Adaptation")
        self.adaptation_id = adaptation_id
        self.adaptation_type = adaptation_type
        self.time = time
        self.change = change
        self.initiator = initiator