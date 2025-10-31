"""
This file contains all functions with queries to be executed by the record.py file
Each function receives tx transaction object because all queries must be executed in that transaction
The return type for all these functions is void
"""


def create_process(tx, id_num):
    """
    This function creates a process node in the database. MERGE ensures creating only unique nodes

    :param id_num: ID of the process
    """
    tx.run("MERGE (:Process {id: $id_num})", id_num=id_num)


def create_event(tx, event):
    """
    This function creates an event node in the database

    :param event: the event to be created
    """
    tx.run("MERGE (:Event {id: $id, name: $name, time: $time, resource: $resource})", id=event.event_id,  name=event.name, time=event.time, resource=event.resource)

def create_adaptation(tx, adaptation):
    """
    This function creates an adaptation node in the database

    :param adaptation: the adaptation to be created
    """
    tx.run("MERGE (:Adaptation {id: $id, type: $adaptation_type, time: $time, change: $change})", id=adaptation.adaptation_id, adaptation_type=adaptation.adaptation_type, time=adaptation.time, change=adaptation.change)

def create_instance(tx, instance_id):
    """
    This function creates a node of a process instance in the database

    :param instance_id: the ID of the instance
    """
    tx.run("MERGE (:Instance {id: $instance_id})", instance_id=instance_id)

def create_initiator(tx, initiator_name):
    """
    This function creates an initiator node in the database

    :param initiator_name: the name of the initiator
    """

    tx.run("MERGE (:Initiator {name: $initiator_name})", initiator_name=initiator_name)


def create_instance_process_relationship(tx, instance_id, process_id):
    """
    This function creates a relationships between a process and an instance in the database

    :param instance_id: the ID of the instance
    :param process_id: the ID of the process
    """
    tx.run("""
        MATCH (process:Process {id: $process_id}), (instance:Instance {id: $instance_id})
        MERGE (instance)-[:INSTANCE_OF]->(process)
    """, process_id=process_id, instance_id=instance_id)


def create_event_instance_relationship(tx, event, instance_id):
    """
    This function creates a relationship between an event and an instance in the database

    :param event: the event object
    :param instance_id: the ID of the instance
    """

    tx.run("""
        MATCH (event:Event{id: $id}), (instance:Instance {id: $instance_id})
        MERGE (event)-[:STEP_OF]->(instance)
    """, id=event.event_id, instance_id=instance_id)

def create_adaptation_event_relationship(tx, adaptation, event):
    """
    This function creates a relationship between an event and an adaptation in the database

    :param adaptation: the adaptation object
    :param event: the event object
    """

    tx.run("""
        MATCH (adaptation:Adaptation{id: $id_adapt}), (event:Event{id: $id_event})
        MERGE (adaptation)-[:APPLIED_TO]->(event)
    """, id_adapt=adaptation.adaptation_id, id_event=event.event_id)

def create_initiator_adaptation_relationship(tx, initiator, adaptation):
    """
    This function creates a relationship between an initiator and an adaptation in the database

    :param initiator: the initiator of the adaptation object
    :param adaptation: the adaptation object
    """
    tx.run("""
        MATCH (initiator:Initiator{name: $initiator_name}), (adaptation:Adaptation{id: $id})
        MERGE (initiator)-[:INVOKES]->(adaptation)
    """, initiator_name=initiator.name, id=adaptation.adaptation_id)
