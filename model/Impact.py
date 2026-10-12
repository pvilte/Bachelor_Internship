from model.Node import Node

class Impact(Node):
    """
    This class describes Impact which is the impact that an Instance has. Therefore, the impact has an instance.
    The superclass is Node.

    :param impact_id: the ID of unique impact
    :param instance_id: the ID of the instance the impact belongs to
    :param impact_type: the type of the impact
    :param name: the actual impact specified
    """

    def __init__(self, impact_id, instance_id, impact_type, name):
        super().__init__("Impact")
        self.impact_id = impact_id
        self.instance_id = instance_id
        self.impact_type = impact_type
        self.name = name