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


def create_event(tx, name, time, resource):
    """
    This function creates an event node in the database

    :param name: name of the event
    :param time: time of the event
    :param resource: the name of the resource carrying out the event
    """
    tx.run("MERGE (:Event {name: $name, time: $time, resource: $resource})", name=name, time=time, resource=resource)

def create_adaptation(tx, ad_type, time, change):
    """
    This function creates an adaptation node in the database

    :param ad_type: type of adaptation
    :param time: time when the adaptation occurs
    :param change: what exactly was changed
    """
    tx.run("MERGE (:Adaptation {type: $adaptation_type, time: $time, change: $change})", adaptation_type=ad_type, time=time, change=change)

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

    :param instance_id: the ID of the instance
    :param event: the event object
    """

    tx.run("""
        MATCH (event:Event{name: $name, time: $time, resource: $resource}), (instance:Instance {id: $instance_id})
        MERGE (event)-[:STEP_OF]->(instance)
    """, name=event.name, time=event.time, resource=event.resource, instance_id=instance_id)

def create_adaptation_event_relationship(tx, adaptation, event):
    """
    This function creates a relationship between an event and an adaptation in the database

    :param adaptation: the adaptation object
    :param event: the event object
    """

    tx.run("""
        MATCH (adaptation:Adaptation{type: $adaptation_type, time: $time, change: $change}), (event:Event{name: $name, time: $time_event, resource: $resource})
        MERGE (adaptation)-[:APPLIED_TO]->(event)
    """, adaptation_type= adaptation.adaptation_type, time=adaptation.time, change=adaptation.change, name=event.name, time_event=event.time, resource=event.resource)

def create_initiator_adaptation_relationship(tx, initiator, adaptation):
    """
    This function creates a relationship between an initiator and an adaptation in the database

    :param initiator: the initiator of the adaptation object
    :param adaptation: the adaptation object
    """
    tx.run("""
        MATCH (initiator:Initiator{name: $initiator_name}), (adaptation:Adaptation{type: $adaptation_type, time: $time, change: $change})
        MERGE (initiator)-[:INVOKES]->(adaptation)
    """, initiator_name=initiator.name, adaptation_type=adaptation.adaptation_type, time=adaptation.time, change=adaptation.change)
