"""
This file contains all queries to be executed by the record.py file
"""


def create_process(tx, id_num):
    tx.run("MERGE (:Process {id: $id_num})", id_num=id_num)


def create_event(tx, name, time, resource):
    tx.run("MERGE (:Event {name: $name, time: $time, resource: $resource})", name=name, time=time, resource=resource)

def create_adaptation(tx, ad_type, time, change):
    tx.run("MERGE (:Adaptation {type: $adaptation_type, time: $time, change: $change})", adaptation_type=ad_type, time=time, change=change)

def create_instance(tx, instance_id):
    tx.run("MERGE (:Instance {id: $instance_id})", instance_id=instance_id)

def create_initiator(tx, initiator_name):
    tx.run("MERGE (:Initiator {name: $initiator_name})", initiator_name=initiator_name)


def create_instance_process_relationship(tx, instance_id, process_id):
    tx.run("""
        MATCH (process:Process {id: $process_id}), (instance:Instance {id: $instance_id})
        MERGE (instance)-[:INSTANCE_OF]->(process)
    """, process_id=process_id, instance_id=instance_id)


def create_event_instance_relationship(tx, event, instance_id):
    tx.run("""
        MATCH (event:Event{name: $name, time: $time, resource: $resource}), (instance:Instance {id: $instance_id})
        MERGE (event)-[:STEP_OF]->(instance)
    """, name=event.name, time=event.time, resource=event.resource, instance_id=instance_id)

def create_adaptation_event_relationship(tx, adaptation, event):
    tx.run("""
        MATCH (adaptation:Adaptation{type: $adaptation_type, time: $time, change: $change}), (event:Event{name: $name, time: $time_event, resource: $resource})
        MERGE (adaptation)-[:APPLIED_TO]->(event)
    """, adaptation_type= adaptation.adaptation_type, time=adaptation.time, change=adaptation.change, name=event.name, time_event=event.time, resource=event.resource)

def create_initiator_adaptation_relationship(tx, initiator, adaptation):
    tx.run("""
        MATCH (initiator:Initiator{name: $initiator_name}), (adaptation:Adaptation{type: $adaptation_type, time: $time, change: $change})
        MERGE (initiator)-[:INVOKES]->(adaptation)
    """, initiator_name=initiator.name, adaptation_type=adaptation.adaptation_type, time=adaptation.time, change=adaptation.change)
