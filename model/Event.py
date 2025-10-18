from model.Instance import Instance


class Event(Instance):
    def __init__(self, name, time, resource, instance_id=None, process_id=None):
        super().__init__(instance_id, process_id)
        self.label = "Event"
        self.name = name
        self.time = time
        self.resource = resource