from model.Process import Process

class Instance(Process):
    """
    This class describes Instance - one run of a Process. Therefore, the superclass is Process.

    :param instance_id: the ID of the instance
    :param id_proc: the ID of the Process associated with the instance, default None
    :param label: the label for Instance in the database
    """

    def __init__(self, instance_id, id_proc=None):
        super().__init__(id_proc)
        self.__label = "Instance"
        self.instance_id = instance_id

