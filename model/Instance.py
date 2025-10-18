from model.Process import Process


class Instance(Process):
    def __init__(self, instance_id, id_proc=None):
        super().__init__(id_proc)
        self.label = "Instance"
        self.instance_id = instance_id

