import json
import os
from time import strptime

from neo4j import GraphDatabase
import re

from model.Event import Event
from model.Initiator import Initiator
from model.Adaptation import Adaptation
from . import queries

uri = "bolt://localhost:7687"
auth = ("neo4j", "internship123")

time_format = "%y/%m/%d %H:%M:%S.%f"

def run_query(query_func, *args):
    driver = GraphDatabase.driver(uri=uri, auth=auth)
    with driver.session() as session:
        session.execute_write(query_func, *args)
    driver.close()


def populate_database(e, file_name):
    adaptation = None
    initiator = None

    # I try to find process by looking at the ID
    # If I find an explicitly given process ID, I should replace the default
    if "processId" in e:
        process_id = e.get("processId")
    else:
        process_id = file_name

    # I try to find an instance
    # If there is no instance ID given, then I just give the file name + "_instance"
    # That's because I just assume there is one instance of the process in that case
    if "instanceId" in e:
        instance_id = e.get("instanceId")
    else:
        instance_id = file_name + "_instance"

    # Event has properties name, time, resource
    # Get these properties and create an event object
    event = Event(e.get("concept:name", ""), strptime(e.get("time:timestamp", ""), time_format), e.get("org:resource", ""), instance_id, process_id)

    run_query(queries.create_process, process_id)
    run_query(queries.create_instance, instance_id)
    run_query(queries.create_event, event.name, event.time, event.resource)

    # I try to find any label that starts with 'adaptation:type' or 'adaptation:change'
    if any(re.match(r"adaptation:(type|change)", key) for key in e.keys()):
        adaptation = Adaptation(e.get("adaptation:type", ""), e.get("adaptation:timestamp", ""),
                                e.get("adaptation:change", ""))
        run_query(queries.create_adaptation, adaptation.adaptation_type, adaptation.time, adaptation.change)

    # I have to fill in also the initiator class
    if "adaptation:initiator" in e:
        initiator = Initiator(e.get("adaptation:initiator", ""))
        run_query(queries.create_initiator, initiator.name)


    # Now I create the relationships
    run_query(queries.create_instance_process_relationship, instance_id, process_id)

    run_query(queries.create_event_instance_relationship, event, instance_id)

    if adaptation is not None:
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
            file_name = file.replace(".json", "")
            with open(file_path, "r", encoding="utf-8") as f:
                #Load the data from the JSON file
                data = json.load(f)

            for case in data:

                #Loop through all events
                for e in case["events"]:
                    populate_database(e, file_name)





if __name__ == "__main__":
    record("../json_files")