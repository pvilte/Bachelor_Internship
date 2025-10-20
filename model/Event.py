from model.Instance import Instance

class Event(Instance):
    """
    This class describes Event - one step of a Process Instance execution, therefore, the superclass is Instance.

    :param name: name of the event
    :param time: time of the event
    :param: resource: the name of the resource that carries out the event
    :param instance_id: the ID of the instance that this process is a step of, default value None
    :param process_id: the ID of the process that the instance is replicating, default value None
    :param label: the label for Event in the database
    """

    def __init__(self, name, time, resource, instance_id=None, process_id=None):
        super().__init__(instance_id, process_id)
        self.__label = "Event"
        self.name = name
        self.time = time
        self.resource = resource