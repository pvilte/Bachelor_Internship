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

def create_events_processes_initiators(e, file_name, stored, inst_counter):
    """
    This function creates events, processes, initiators, for a given event.

    :param e: event object
    :param file_name: name of the file
    :param stored: the dictionary of stored processes, instances, events, initiators, adaptations
    :param inst_counter: the number of instances this far
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
        instance_id = file_name + "_instance_" + str(inst_counter)

    stored_process = stored["processes"].get(process_id, None)
    stored_instance = stored["instances"].get(instance_id, None)

    instance = stored_instance
    process = stored_process
    if stored_process is None and stored_instance is None:
        # Create a new process and a new instance, link them to the event
        process = Process(process_id)
        instance = Instance(instance_id, process)
        stored["instances"][instance_id] = instance
        stored["processes"][process_id] = process

    elif stored_instance is None:
        # Create a new instance, link it to the already existing process, link the event to the instance
        instance = Instance(instance_id, stored_process)
        stored["instances"][instance_id] = instance
    else:
        # The process is not stored
        process = Process(process_id)
        stored_instance.process = process
        stored["processes"][process_id] = process

    # Link the event to the instance (instance has been linked to the process when it was created)
    event_id = file_name + "_event_" + str(len(stored["events"]))
    event = Event(event_id, e.get("concept:name", ""),
                  find_time(e.get("time:timestamp")), e.get("org:resource", ""),
                  instance)
    stored["events"][event_id] = event
    return process, instance, event


def create_adaptations_initiators(file_name, e, stored):
    """
    This function finds initiators and adaptations in the event. It ensures that each adaptation
    has an initiator using composition.

    :param file_name: the name of the file
    :param e: the event object
    :param stored: the dictionary of stored processes, instances, events, initiators, adaptations
    :return initiator, adaptation: the initiator and adaptation objects from the event
    """

    if "adaption:initiator" in e:
        initiator_name = e.get("adaption:initiator")
    elif "adaptation:initiator" in e:
        initiator_name = e.get("adaptation:initiator")
    else:
        initiator_name = file_name + "_unknown_initiator_"

    stored_initiator = stored["initiators"].get(initiator_name, None)


    if stored_initiator:
        initiator = stored_initiator
    else:
        initiator = Initiator(initiator_name)
        stored["initiators"][initiator_name] = initiator

    adaptation_id = file_name + "_adaptation_" + str(len(stored["adaptations"]))
    adaptation = Adaptation(adaptation_id, e.get("adaptation:type", ""),
                            find_time(e.get("adaptation:timestamp")), e.get("adaptation:change", ""),
                            initiator)
    stored["adaptations"][adaptation_id] = adaptation

    return initiator, adaptation


def populate_database(e, file_name, stored, inst_counter):

    """
    This function populates the database with the event information.

    :param e: event object
    :param file_name: name of the file to give an ID to a process in case no ID is given in the event
    :param stored: the dictionary of stored processes, instances, events, initiators, adaptations
    :param inst_counter: number of traces this far
    :return: void
    """

    process, instance, event = create_events_processes_initiators(e, file_name, stored, inst_counter)

    # Create nodes
    run_query(queries.create_event, event)
    run_query(queries.create_process, process)
    run_query(queries.create_instance, instance)
    # Create relationships
    run_query(queries.create_instance_process_relationship, instance, process)
    run_query(queries.create_event_instance_relationship, event, instance)

    # If any label starts with 'adaptation:type' or 'adaptation:change', or 'adaptation:time', an adaptation has happened
    if any(re.match(r"adaptation:(type|change|time)", key) for key in e.keys()):
        initiator, adaptation = create_adaptations_initiators(file_name, e, stored)
        # Create nodes
        run_query(queries.create_adaptation, adaptation)
        run_query(queries.create_initiator, initiator)
        # Create relationships
        run_query(queries.create_adaptation_event_relationship, adaptation, event)
        run_query(queries.create_initiator_adaptation_relationship, initiator, adaptation)

    # If this is not the 0th or the 1st event in the file, create the time relationship between this event and
    # the previous one
    if len(stored["events"]) > 1:
        run_query(queries.create_event_time_relationship, event, list(stored["events"].values())[-2])
    # If this is not the 0th or the 1st event in the file, create the time relationship between this instance and
    # the previous one
    if len(stored["instances"]) > 1:
        run_query(queries.create_instance_time_relationship, instance, list(stored["instances"].values())[-2])


def record(json_dir):

    """
    This function goes through the JSON files and tries to find an event. If it is found, it can be stored in d database

    :param json_dir: the name of the directory containing the JSON files
    :return: void
    """

    # Counter used to keep track how many traces - instances there are
    inst_counter = 0

    # Used for keeping track which processes, instances, initiators, events, adaptations have already been stored
    stored = {
        "processes": {},
        "instances": {},
        "initiators": {},
        "events": {},
        "adaptations": {}
    }
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
                    populate_database(e, file_name, stored, inst_counter)
                inst_counter += 1


            # Clear the dictionary for the next file
            for key in stored:
                stored[key] = {}



if __name__ == "__main__":
    # Change the parameter here based on your environment
    record("json_files")
    print("Record complete!\n")