import json
import os
from datetime import datetime
from neo4j import GraphDatabase
import re
from model.Event import Event
from model.Initiator import Initiator
from model.Adaptation import Adaptation
from . import queries

# Change the values here based on your environment
uri = "bolt://localhost:7687"
auth = ("neo4j", "internship123")


def run_query(query_func, *args):

    """
    This function creates a connection to a neo4j database, creates a session, and executes a write query.
    Then, the driver is closed to release any resources still held by it.

    :param query_func: the function to execute; these functions reside in queries.py directory
    :param args: unfixed number of arguments to be given to the query function
    :return: void
    """

    driver = GraphDatabase.driver(uri=uri, auth=auth)
    with driver.session() as session:
        session.execute_write(query_func, *args)
    driver.close()


def populate_database(e, file_name):

    """
    This function populates the database with the event information.

    :param e: event object
    :param file_name: name of the file to give an ID to a process in case no ID is given in the event
    :return: void
    """

    # Assume a regular event with no adaptations and adaptation initiators
    adaptation = None
    initiator = None

    # If an ID of a process is given in the event, save the ID of the process; if not, give the ID as the file name
    # If any event is written in the XES file, there must be a process and an instance the event is a part of
    if "processId" in e:
        process_id = e.get("processId")
    else:
        process_id = file_name

    if "instanceId" in e:
        instance_id = e.get("instanceId")
    else:
        instance_id = file_name + "_instance"


    event = Event(e.get("concept:name", ""), datetime.fromisoformat(e.get("time:timestamp", "")), e.get("org:resource", ""), instance_id, process_id)
    run_query(queries.create_process, process_id)
    run_query(queries.create_instance, instance_id)
    run_query(queries.create_event, event.name, event.time, event.resource)

    # If any label starts with 'adaptation:type' or 'adaptation:change', an adaptation has happened
    # There must be an initiator
    if any(re.match(r"adaptation:(type|change)", key) for key in e.keys()):
        adaptation = Adaptation(e.get("adaptation:type", ""), datetime.fromisoformat(e.get("adaptation:timestamp", "")), e.get("adaptation:change", ""))
        run_query(queries.create_adaptation, adaptation.adaptation_type, adaptation.time, adaptation.change)
        initiator = Initiator(e.get("adaptation:initiator", ""))
        run_query(queries.create_initiator, initiator.name)


    # Nodes are created, create relationships
    run_query(queries.create_instance_process_relationship, instance_id, process_id)
    run_query(queries.create_event_instance_relationship, event, instance_id)

    if adaptation is not None:
        run_query(queries.create_adaptation_event_relationship, adaptation, event)
    if initiator is not None and adaptation is not None:
        run_query(queries.create_initiator_adaptation_relationship, initiator, adaptation)

def record(json_dir):

    """
    This function goes through the JSON files and tries to find an event. If it is found, it can be stored in d database

    :param json_dir: the name of the directory containing the JSON files
    :return: void
    """

    # Go through every subdirectory of the directory of the JSON files
    for path, folders, files in os.walk(json_dir):
        for file in files:
            file_path = os.path.join(path, file)
            file_name = file.replace(".json", "")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for case in data:
                for e in case["events"]:
                    # An event is found, call the function to populate the database
                    populate_database(e, file_name)





if __name__ == "__main__":
    # Change the parameter here based on your environment
    record("../json_files")