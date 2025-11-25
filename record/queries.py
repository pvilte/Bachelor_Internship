"""
This file contains all functions with queries to be executed by the record.py file
Each function receives tx transaction object because all queries must be executed in that transaction
The return type for all these functions is void
"""


def create_process(tx, process):
    """
    This function creates a process node in the database. MERGE ensures creating only unique nodes

    :param process: the process object
    """
    tx.run("MERGE (:Process {id: $id_num})", id_num=process.id_proc)


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

def create_instance(tx, instance):
    """
    This function creates a node of a process instance in the database

    :param instance: the instance object
    """
    tx.run("MERGE (:Instance {id: $instance_id})", instance_id=instance.instance_id)

def create_initiator(tx, initiator):
    """
    This function creates an initiator node in the database

    :param initiator: the initiator object
    """

    tx.run("MERGE (:Initiator {name: $initiator_name})", initiator_name=initiator.name)


def create_instance_process_relationship(tx, instance, process):
    """
    This function creates a relationships between a process and an instance in the database

    :param instance: the instance object
    :param process: the process object
    """
    tx.run("""
        MATCH (process:Process {id: $process_id}), (instance:Instance {id: $instance_id})
        MERGE (instance)-[:INSTANCE_OF]->(process)
    """, process_id=process.id_proc, instance_id=instance.instance_id)


def create_event_instance_relationship(tx, event, instance):
    """
    This function creates a relationship between an event and an instance in the database

    :param event: the event object
    :param instance: the instance object
    """

    tx.run("""
        MATCH (event:Event{id: $id}), (instance:Instance {id: $instance_id})
        MERGE (event)-[:STEP_OF]->(instance)
    """, id=event.event_id, instance_id=instance.instance_id)

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

def create_event_time_relationship(tx, curr_event, prev_event):
    """"
    This function creates a time relationship between an event and its previous event

    :param curr_event: the current event
    :param prev_event: the previous event
    """
    tx.run("""
        MATCH (curr_event:Event{id: $id_curr_event}), (prev_event:Event{id: $id_prev_event})
        MERGE (curr_event)<-[:BEFORE]-(prev_event)
    """, id_curr_event=curr_event.event_id, id_prev_event=prev_event.event_id)

