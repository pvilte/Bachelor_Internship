from model.Instance import Instance

class Event(Instance):
    """
    This class describes Event - one step of a Process Instance execution, therefore, the superclass is Instance.

    Attributes:
        name(string) - name of the event
        time(datetime) - time of the event
        resource(string) - the name of the resource that carries out the event
        instance_id(string) - the ID of the instance that this process is a step of, default value None
        process_id(string) - the ID of the process that the instance is replicating, default value None
        label(string) - the label for Event in the database
    """

    def __init__(self, name, time, resource, instance_id=None, process_id=None):
        super().__init__(instance_id, process_id)
        self.label = "Event"
        self.name = name
        self.time = time
        self.resource = resource