import json
import os
from neo4j import GraphDatabase
import re

from model.Event import Event
from model.Initiator import Initiator
from model.Instance import Instance
from model.Process import Process
from model.Adaptation import Adaptation

uri = "bolt://localhost:7687"
auth = ("neo4j", "internship123")

def create_update_process(tx, name, id_num=None):
    if id_num is None:
        tx.run("MERGE (:Process {name: $name})", name=name)
    else:
        tx.run("""
            MERGE (p:Process {name: $name})
            SET p.id = $id_num
        """, name=name, id_num=id_num)


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


def record(json_dir):
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        #Go through every subdirectory of the directory of the JSON files
        for path, folders, files in os.walk(json_dir):
            #Go through all files in the file list
            for file in files:
                #Merge the directory with the file name
                file_path = os.path.join(path, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    #Load the data from the JSON file
                    data = json.load(f)

                #Instanitate the process, the process ID for now is the name of the file
                file_name = file.replace(".json", "")
                process = Process(None, file_name)
                session.execute_write(create_update_process, process.name)

                for case in data:

                    #Loop through all events
                    for e in case["events"]:
                        instance_id = None
                        process_id = None
                        adaptation = None
                        initiator = None
                        event = None


                        #Event has properties name, time, resource
                        #Get these properties and create an event object
                        event = Event(e.get("concept:name", ""), e.get("time:timestamp", ""), e.get("org:resource", ""))
                        #Create the node of the event in the database
                        session.execute_write(create_event, event.name, event.time, event.resource)

                        #I try to find any label that starts with 'adaptation:type' or 'adaptation:change'
                        if any(re.match(r"adaptation:(type|change)", key) for key in e.keys()):
                            adaptation = Adaptation(e.get("adaptation:type", ""), e.get("adaptation:timestamp", ""), e.get("adaptation:change", ""))
                            session.execute_write(create_adaptation, adaptation.adaptation_type, adaptation.time, adaptation.change)


                        #In a similar way, I should try to find instance
                        if "instanceId" in e:
                            instance = Instance(e.get("instanceId", ""))
                            session.execute_write(create_instance, instance.instance_id)
                            instance_id = instance.instance_id

                        #Now I try to find process
                        if "processId" in e:
                            process = Process(e.get("processId", ""), file_name)
                            session.execute_write(create_update_process, file_name, process.id_number)
                            process_id = process.id_number

                        #I have to fill in also the initiator class
                        if "adaptation:initiator" in e:
                            initiator = Initiator(e.get("adaptation:initiator", ""))
                            session.execute_write(create_initiator, initiator.name)


                        #Now I create the relationships
                        if instance_id is not None and process_id is not None:
                            session.execute_write(create_instance_process_relationship, instance_id, process_id)

                        if event is not None and instance_id is not None:
                            session.execute_write(create_event_instance_relationship, event, instance_id)

                        if adaptation is not None and event is not None:
                            session.execute_write(create_adaptation_event_relationship, adaptation, event)

                        if initiator is not None and adaptation is not None:
                            session.execute_write(create_initiator_adaptation_relationship, initiator, adaptation)


    driver.close()


if __name__ == "__main__":
    record("./json_files")