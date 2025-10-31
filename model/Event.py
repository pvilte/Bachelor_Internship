from model.Node import Node

class Event(Node):
    """
    This class describes Event - one step of a Process Instance execution, therefore, the superclass is Instance.

    :param event_id: the ID of the event
    :param name: name of the event
    :param time: time of the event
    :param: resource: the name of the resource that carries out the event
    :param instance: the instance that this process is a step of
    """

    def __init__(self, event_id, name, time, resource, instance):
        super().__init__("Event")
        self.event_id = event_id
        self.name = name
        self.time = time
        self.resource = resource
        self.instance = instance