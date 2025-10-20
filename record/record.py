import json
import os
from datetime import datetime
from neo4j import GraphDatabase
import re
from model.Event import Event
from model.Initiator import Initiator
from model.Adaptation import Adaptation
from model.Instance import Instance
from model.Process import Process
from . import queries

# Change the values here based on your environment
uri = "bolt://127.0.0.1:7687"
auth = ("neo4j", "internship123")

def find_time(time):
    """
    This function tries to convert the datatype from JSON string to time. If it is not successful, return current time
    :param time: JSON string representing time
    :return: final time as a datetime object
    """
    try:
        result_time = datetime.fromisoformat(time)
    except:
        result_time = datetime.now()

    return result_time

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


def populate_database(e, file_name, processes, instances):

    """
    This function populates the database with the event information. It uses composition to ensure
    that each process has an instance, each instance has a process.

    :param e: event object
    :param file_name: name of the file to give an ID to a process in case no ID is given in the event
    :param processes: dictionary of already stored processes
    :param instances: dictionary of already stored instances
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

    stored_process = processes.get(process_id, None)
    stored_instance = instances.get(instance_id, None)

    if stored_process and stored_instance:
        # Link the event to the instance
        event = Event(e.get("concept:name", ""), find_time(e.get("time:timestamp")), e.get("org:resource", ""),
                  stored_instance)
    elif stored_process is None and stored_instance is None:
        # Create a new process and a new instance, link them to the event
        process = Process(process_id)
        instance = Instance(instance_id, process)
        event = Event(e.get("concept:name", ""), find_time(e.get("time:timestamp")), e.get("org:resource", ""),
                      instance)
        instances[instance_id] = instance
        processes[process_id] = process
        run_query(queries.create_process, process_id)
        run_query(queries.create_instance, instance_id)
    elif stored_instance is None:
        # Create a new instance, link it to the already existing process, link the event to the instance
        instance = Instance(instance_id, stored_process)
        event = Event(e.get("concept:name", ""), find_time(e.get("time:timestamp")), e.get("org:resource", ""),
                      instance)
        instances[instance_id] = instance
        run_query(queries.create_instance, instance_id)
    else:
        # The process is not stored
        process = Process(process_id)
        stored_instance.process = process
        event = Event(e.get("concept:name", ""), find_time(e.get("time:timestamp")), e.get("org:resource", ""),
                      stored_instance)
        processes[process_id] = process
        run_query(queries.create_process, process_id)


    run_query(queries.create_event, event.name, event.time, event.resource)

    # If any label starts with 'adaptation:type' or 'adaptation:change', or 'adaptation:time', an adaptation has happened
    # There must be an initiator
    if any(re.match(r"adaptation:(type|change|time)", key) for key in e.keys()):
        adaptation = Adaptation(e.get("adaptation:type", ""), find_time(e.get("adaptation:timestamp")), e.get("adaptation:change", ""))
        run_query(queries.create_adaptation, adaptation.adaptation_type, adaptation.time, adaptation.change)
        # Sometimes it is written as 'adaption:initiator', sometimes "adaptation:initiator"
        initiator_name = e.get("adaptation:initiator", "") or e.get("adaption:initiator", "")
        if initiator_name == "":
            initiator_name = "Unknown"
        initiator = Initiator(initiator_name)
        run_query(queries.create_initiator, initiator.name)


    # Create relationships
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

    processes = {}
    instances = {}
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
                    populate_database(e, file_name, processes, instances)



if __name__ == "__main__":
    # Change the parameter here based on your environment
    record("json_files")