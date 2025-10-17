import json
import os
from neo4j import GraphDatabase
import re

from model.Event import Event
from model.Initiator import Initiator
from model.Instance import Instance
from model.Process import Process
from model.Adaptation import Adaptation
from . import queries

uri = "bolt://localhost:7687"
auth = ("neo4j", "internship123")

def run_query(query_func, *args):
    driver = GraphDatabase.driver(uri=uri, auth=auth)
    with driver.session() as session:
        session.execute_write(query_func, *args)
    driver.close()


def populate_database(e, file_name):
    instance_id = None
    process_id = None
    adaptation = None
    initiator = None
    event = None

    # Event has properties name, time, resource
    # Get these properties and create an event object
    event = Event(e.get("concept:name", ""), e.get("time:timestamp", ""), e.get("org:resource", ""))
    # Create the node of the event in the database
    run_query(queries.create_event, event.name, event.time, event.resource)

    # I try to find any label that starts with 'adaptation:type' or 'adaptation:change'
    if any(re.match(r"adaptation:(type|change)", key) for key in e.keys()):
        adaptation = Adaptation(e.get("adaptation:type", ""), e.get("adaptation:timestamp", ""),
                                e.get("adaptation:change", ""))
        run_query(queries.create_adaptation, adaptation.adaptation_type, adaptation.time, adaptation.change)

    # In a similar way, I should try to find instance
    if "instanceId" in e:
        instance = Instance(e.get("instanceId", ""))
        run_query(queries.create_instance, instance.instance_id)
        instance_id = instance.instance_id

    # Now I try to find process
    if "processId" in e:
        process = Process(e.get("processId", ""), file_name)
        run_query(queries.create_update_process, file_name, process.id_number)
        process_id = process.id_number

    # I have to fill in also the initiator class
    if "adaptation:initiator" in e:
        initiator = Initiator(e.get("adaptation:initiator", ""))
        run_query(queries.create_initiator, initiator.name)

    # Now I create the relationships
    if instance_id is not None and process_id is not None:
        run_query(queries.create_instance_process_relationship, instance_id, process_id)

    if event is not None and instance_id is not None:
        run_query(queries.create_event_instance_relationship, event, instance_id)

    if adaptation is not None and event is not None:
        run_query(queries.create_adaptation_event_relationship, adaptation, event)

    if initiator is not None and adaptation is not None:
        run_query(queries.create_initiator_adaptation_relationship, initiator, adaptation)

def record(json_dir):
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
            run_query(queries.create_update_process, process.name)

            for case in data:

                #Loop through all events
                for e in case["events"]:
                    populate_database(e, file_name)





if __name__ == "__main__":
    record("../json_files")