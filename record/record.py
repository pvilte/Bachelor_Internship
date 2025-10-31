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


uri = os.getenv("NEO4J_URI")
auth = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

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

def create_events_processes_initiators(e, file_name, counter, processes, instances):
    """
    This function creates events, processes, initiators, for a given event.

    :param e: event object
    :param file_name: name of the file
    :param counter: counter dictionary, used for assigning IDs
    :param processes: already stored processes
    :param instances: already stored instances
    :return process, instance, event: the process, instance, and event from the event
    """



    # If an ID of a process is given in the event, save the ID of the process; if not, give the ID as the file name
    # If any event is written in the XES file, there must be a process and an instance the event is a part of
    if "processId" in e:
        process_id = e.get("processId")
    else:
        # Assume file names are unique
        process_id = file_name + "_process_"

    if "instanceId" in e:
        instance_id = e.get("instanceId")
    else:
        # In each file, there could be multiple traces, each trace showing a different instance
        instance_id = file_name + "_instance_" + str(counter["instance"])

    stored_process = processes.get(process_id, None)
    stored_instance = instances.get(instance_id, None)

    instance = stored_instance
    process = stored_process
    if stored_process is None and stored_instance is None:
        # Create a new process and a new instance, link them to the event
        process = Process(process_id)
        instance = Instance(instance_id, process)
        instances[instance_id] = instance
        processes[process_id] = process

    elif stored_instance is None:
        # Create a new instance, link it to the already existing process, link the event to the instance
        instance = Instance(instance_id, stored_process)
        instances[instance_id] = instance
    else:
        # The process is not stored
        process = Process(process_id)
        stored_instance.process = process
        processes[process_id] = process

    # Link the event to the instance (instance has been linked to the process when it was created)
    event = Event(file_name + "_event_" + str(counter["event"]), e.get("concept:name", ""),
                  find_time(e.get("time:timestamp")), e.get("org:resource", ""),
                  instance)
    return process, instance, event


def create_adaptations_initiators(file_name, counter, e, initiators):
    """
    This function finds initiators and adaptations in the event. It ensures that each adaptation
    has an initiator using composition.

    :param file_name: the name of the file
    :param counter: the counter dictionary, used for assigning IDs
    :param e: the event object
    :param initiators: the stored initiators
    :return initiator, adaptation: the initiator and adaptation objects from the event
    """

    if "adaption:initiator" in e:
        initiator_name = e.get("adaption:initiator")
    elif "adaptation:initiator" in e:
        initiator_name = e.get("adaptation:initiator")
    else:
        initiator_name = file_name + "_unknown_initiator_"

    stored_initiator = initiators.get(initiator_name, None)

    initiator = stored_initiator
    if stored_initiator:
        adaptation = Adaptation(file_name + "_adaptation_" + str(counter["adaptation"]), e.get("adaptation:type", ""),
                                find_time(e.get("adaptation:timestamp")), e.get("adaptation:change", ""),
                                stored_initiator)
    else:
        initiator = Initiator(initiator_name)
        adaptation = Adaptation(file_name + "_adaptation_" + str(counter["adaptation"]), e.get("adaptation:type", ""),
                                find_time(e.get("adaptation:timestamp")),
                                e.get("adaptation:change", ""), initiator)
        initiators[initiator_name] = initiator

    counter["adaptation"] += 1
    return initiator, adaptation


def populate_database(e, file_name, processes, instances, initiators, counter):

    """
    This function populates the database with the event information.

    :param e: event object
    :param file_name: name of the file to give an ID to a process in case no ID is given in the event
    :param processes: dictionary of already stored processes
    :param instances: dictionary of already stored instances
    :param initiators: dictionary of already stored initiators
    :param counter: counter dictionary for assigning IDs
    :return: void
    """

    process, instance, event = create_events_processes_initiators(e, file_name, counter, processes, instances)

    # Create nodes
    run_query(queries.create_process, process)
    run_query(queries.create_instance, instance)
    # Create relationships
    run_query(queries.create_event, event)
    run_query(queries.create_instance_process_relationship, instance, process)
    run_query(queries.create_event_instance_relationship, event, instance)

    # If any label starts with 'adaptation:type' or 'adaptation:change', or 'adaptation:time', an adaptation has happened
    if any(re.match(r"adaptation:(type|change|time)", key) for key in e.keys()):
        initiator, adaptation = create_adaptations_initiators(file_name, counter, e, initiators)
        # Create nodes
        run_query(queries.create_adaptation, adaptation)
        run_query(queries.create_initiator, initiator)
        # Create relationships
        run_query(queries.create_adaptation_event_relationship, adaptation, event)
        run_query(queries.create_initiator_adaptation_relationship, initiator, adaptation)


def record(json_dir):

    """
    This function goes through the JSON files and tries to find an event. If it is found, it can be stored in d database

    :param json_dir: the name of the directory containing the JSON files
    :return: void
    """

    # Used for counting the IDs
    counter = {
        "event": 0,
        "adaptation": 0,
        "instance": 0
    }

    # Used for keeping track which processes, instances, initiators have already been stored
    processes = {}
    instances = {}
    initiators = {}
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
                    populate_database(e, file_name, processes, instances, initiators, counter)
                    counter["event"] += 1
                counter["instance"] += 1

            counter["instance"] = 0
            counter["event"] = 0
            counter["adaptation"] = 0



if __name__ == "__main__":
    # Change the parameter here based on your environment
    record("json_files")
    print("Record complete!\n")