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
from model.Impact import Impact
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
        result = session.execute_write(query_func, *args)
    driver.close()
    return result

def create_events_processes_initiators(e, stored):
    """
    This function creates events, processes, initiators, for a given event.

    :param e: event object
    :param file_name: name of the file
    :param stored: the dictionary of stored processes, instances, events, initiators, adaptations
    :param inst_counter: the number of instances this far
    :param stored_instances: dictionary to keep track which instance_id's have already been used by previous files
    :return process, instance, event: the process, instance, and event from the event
    """

    # If an ID of a process is given in the event, save the ID of the process; if not, give the ID as the file name
    # If any event is written in the XES file, there must be a process and an instance the event is a part of
    if "processId" in e:
        process_id = e.get("processId")
    else:
        # Assume file names are unique
        # process_id = file_name + "_process_"
        raise Exception("Missing process ID in data")

    if "instanceId" in e:
        instance_id = e.get("instanceId")
    else:
        # In each file, there could be multiple traces, each trace showing a different instance
        # instance_id = file_name + "_instance_" + str(inst_counter)
        raise Exception("Missing instance ID in data")

    # There should be one process and instance per run:
    stored_process = stored["processes"].get(process_id, None)
    stored_instance = stored["instances"].get(instance_id, None)

    instance = stored_instance
    process = stored_process

    # Create a flag we can use to track whether the instance has been recoded before.
    new_instance = False

    # TODO implementation of dealing with duplicate instance IDs when traces are produced by different workflow engines

    if stored_process is None and stored_instance is None:
        # Create a new process and a new instance, link them to the event
        process = Process(process_id)
        instance = Instance(instance_id, process)
        stored["instances"][instance_id] = instance
        stored["processes"][process_id] = process

        # Set instance flag to True as we have found an instance we haven't encountered before in this run:
        new_instance = True

    elif stored_instance is None:
        # Create a new instance, link it to the already existing process, link the event to the instance
        instance = Instance(instance_id, stored_process)
        stored["instances"][instance_id] = instance

        # Set instance flag to True as we have found an instance we haven't encountered before in this run:
        new_instance = True
        
    else:
        # The process is not stored
        process = Process(process_id)
        stored_instance.process = process
        stored["processes"][process_id] = process

    # Link the event to the instance (instance has been linked to the process when it was created)
    event_id = instance_id + "_event_" + str(len(stored["events"]))

    # Check if event name exist and is not empty in file, otherwise, raise an exception:
    if "concept:name" in e:
        event_name = e.get("concept:name")
        if event_name == "":
            raise Exception(f"Instance with ID {instance_id} has an event with a missing concept:name field")
    else:
        raise Exception(f"Instance with ID {instance_id} has an event with a missing concept:name field")

    # Check if event timestamp exists in file, otherwise, raise an exception:
    if "time:timestamp" in e:
        timestamp = find_time(e.get("time:timestamp"))
    elif "adaptation:timestamp" in e:
        # if event was deleted, event never happened, thus, the field is empty:
        timestamp = ""
    else:
        raise Exception(f"Instance with ID {instance_id} has an event with a missing time:timestamp field")

    # Check if event resource exists and is not empty in file, otherwise, raise an exception:
    if "org:resource" in e:
        resource = e.get("org:resource")
        if resource == "":
            raise Exception(f"Instance with ID {instance_id} has an event with a missing org:resource field")
    elif "adaptation:type" in e:
        # if event was deleted, it was not executed by a resource, thus, the field is empty:
        resource = ""
    else:
        raise Exception(f"Instance with ID {instance_id} has an event with a missing org:resource field")
    
    
    event = Event(event_id, event_name, timestamp, resource, instance)
    stored["events"][event_id] = event
    return process, instance, event, new_instance


def create_adaptations_initiators(e, stored):
    """
    This function finds initiators and adaptations in the event. It ensures that each adaptation
    has an initiator using composition.

    :param file_name: the name of the file
    :param e: the event object
    :param stored: the dictionary of stored processes, instances, events, initiators, adaptations
    :return initiator, adaptation: the initiator and adaptation objects from the event
    """

    # Find the instance ID which will be used for naming purposes:
    if "instanceId" in e:
        instance_id = e.get("instanceId")
    else:
        raise Exception("Missing instance ID in data")
    

    if "adaption:initiator" in e:
        initiator_name = e.get("adaption:initiator")
    elif "adaptation:initiator" in e:
        initiator_name = e.get("adaptation:initiator")
    else:
        # Add the instance as an identifier in the name as instance should be unique for each trace:
        initiator_name = instance_id + "_unknown_initiator_"

    stored_initiator = stored["initiators"].get(initiator_name, None)


    if stored_initiator:
        initiator = stored_initiator
    else:
        initiator = Initiator(initiator_name)
        stored["initiators"][initiator_name] = initiator

    adaptation_id =  instance_id + "_adaptation_" + str(len(stored["adaptations"]))

    # Check if adaptation type exists and is not empty, otherwise, raise an exception:
    if "adaptation:type" in e:
        adaptation_type = e.get("adaptation:type")
        if adaptation_type == "":
            raise Exception(f"Instance with ID {instance_id} has an event with a missing adaptation:type field")
    else :
        raise Exception(f"Instance with ID {instance_id} has an event with a missing adaptation:type field")

    # Check if adaptation timestamp exists, otherwise, raise an exception:
    if "adaptation:timestamp" in e:
        adaptation_timestamp = find_time(e.get("adaptation:timestamp"))
    else :
        raise Exception(f"Instance with ID {instance_id} as an event with a missing adaptation:timestamp field")
    
    # Check if adaptation type exists and is not empty, otherwise, raise an exception:
    if "adaptation:change" in e:
        adaptation_change = e.get("adaptation:change")
        if adaptation_change == "":
            raise Exception(f"Instance with ID {instance_id} as an event with a missing adaptation:change field")
    else :
        raise Exception(f"Instance with ID {instance_id} as an event with a missing adaptation:change field")

    
    adaptation = Adaptation(adaptation_id, adaptation_type, adaptation_timestamp, adaptation_change,
                            initiator, e.get("adaptation:reason", ""), e.get("adaptation:impact", "") )
    stored["adaptations"][adaptation_id] = adaptation

    return initiator, adaptation


def populate_database(e, stored):

    """
    This function populates the database with the event information.

    :param e: event object
    :param file_name: name of the file to give an ID to a process in case no ID is given in the event
    :param stored: the dictionary of stored processes, instances, events, initiators, adaptations
    :param inst_counter: number of traces this far
    :param stored_instances: dictionary to keep track which instance_id's have already been used by previous files
    :return: void
    """

    process, instance, event, new_instance = create_events_processes_initiators(e, stored)

    # create the instance only if it hasn't been created before:
    if new_instance:
        # If there already exists an instance with the given ID, the constraint in database will flag it 
        # and will not proceed.
        run_query(queries.create_instance, instance)

    # Create nodes
    run_query(queries.create_event, event)
    run_query(queries.create_process, process)

    # Create relationships
    run_query(queries.create_instance_process_relationship, instance, process)
    run_query(queries.create_event_instance_relationship, event, instance)

    # If any label starts with 'adaptation:type' or 'adaptation:change', or 'adaptation:time', an adaptation has happened
    if any(re.match(r"adaptation:(type|change|time)", key) for key in e.keys()):
        initiator, adaptation = create_adaptations_initiators(e, stored)
        # Create nodes
        run_query(queries.create_adaptation, adaptation)
        run_query(queries.create_initiator, initiator)
        # Create relationships
        run_query(queries.create_adaptation_event_relationship, adaptation, event)
        run_query(queries.create_initiator_adaptation_relationship, initiator, adaptation)

    # If this is not the 0th or the 1st event in the file, create the time relationship between this event and
    # the previous one
    if len(stored["events"]) > 1:
        all_events = list(stored["events"].values())
        previous_event = all_events[-2]
        # Create the time relationship only between events of the same instances
        if previous_event.instance.instance_id == event.instance.instance_id:
            run_query(queries.create_event_time_relationship, event, list(stored["events"].values())[-2])


def add_impact_to_database(c, stored_impacts):
    """"
    This function records an instance's impact to the database.

    :param c: the data block that includes instance_id, impact and its type
    :param file_name: the name of the file we are accessing
    :param stored_impacts: list of impacts already stored
    """

    instance_id = c.get("instance:id")
    # Check if instance that has this impact has already been recorded in database:
    instance_exists = run_query(queries.check_existing_instance, instance_id)
    if not instance_exists:
        raise Exception(f"The provided instance_id '{instance_id}' does not exist in the database.")

    if "impact:type" in c:
        impact_type = c.get("impact:type")
    else:
        raise Exception(f"Instance with ID {instance_id} has an impact with no impact_type")

    if "impact" in c:
        impact= c.get("impact")
    else:
        raise Exception(f"Instance with ID {instance_id} has an impact with no impact_type")

    # create an impact id unique for each instance:
    n = 1
    while (instance_id + "_impact_" + str(n)) in stored_impacts:
        n += 1
    impact_id = instance_id + "_impact_" + str(n)

    # keep track of impact_ids already taken:
    stored_impacts[impact_id] = True

    impact = Impact(impact_id, instance_id, impact_type, impact)
    run_query(queries.create_impact, impact)
    run_query(queries.create_impact_instance_relationship, impact)


def process_event_data_helper_func(data, impact_data_files, data_count, stored):
    """
    Helper function to reduce code duplication. It takes event data and processes it one by one
    to record it to the database.

    :param data: event data read from .json file or from HTTP request.
    :param impact_data_files: dictionary of stored impacts that are to be proccessed.
    :param file_name: name of file or data that is being processed.
    :param stored: dictionary to keep track of stored objects.
    :param stored_instances: dictionary to specifically keep track of instances already processed in one record() run.
    :param inst_counter: used to keep track of how many instances have already been stored.
    """

    for case in data:
        # check if file just adds input for instances:
        if "instance:id" in case:
            # store the file's contents:
            impact_data_files[data_count] = data 
        else: 
            for e in case["events"]:
                # An event is found, call the function to populate the database
                populate_database(e, stored)



def record_impacts_helper_function(impact_data_files, stored_impacts):
    """
    Helper function to reducce code duplication. Goes through all files and data containing overall impacts
    and adds them to database.

    :param impact_data_files: dictionary of files or data sent from HTTP request that contain overall impacts of instances.
    :param stored_impacts: dictionary to keepo track of instances already recorded.
    """

    # Record impacts of instances in the database if such exist:
    if impact_data_files:
        print("Adding impacts of instances to the database.\n")
        for data_count in impact_data_files:
            for impact in impact_data_files[data_count]:
                add_impact_to_database(impact, stored_impacts)


def record(json_dir):

    """
    This function goes through the JSON files and tries to find an event. If it is found, it can be stored in database.
    This function is used when dealing with files saved in known directory.

    :param json_dir: the name of the directory containing the JSON files
    :return: void
    """

    # Create a unique constraint for instance and event IDs:
    run_query(queries.create_instance_constraint)

    stored_impacts = {}

    # Used for keeping track which processes, instances, initiators, events, adaptations have already been stored
    stored = {
        "processes": {},
        "instances": {},
        "initiators": {},
        "events": {},
        "adaptations": {},
    }

    # Dictionary for storing filename and data of file that contains total impact:
    impact_data_files = {}

    # Go through every subdirectory of the directory of the JSON files
    for path, folders, files in os.walk(json_dir):
        file_counter = 0
        for file in files:
            file_path = os.path.join(path, file)
            file_name = file.replace(".json", "")
            print ("Record: " + file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            process_event_data_helper_func(data, impact_data_files, file_counter, stored)

            # Clear the dictionary for the next file
            for key in stored:
                stored[key] = {}

            file_counter += 1

    # Record impacts of instances in the database if such exist:
    record_impacts_helper_function(impact_data_files, stored_impacts)


def record_from_api(data):
    """
    Function reads JSON data given by an HTTP POST request and stored found event data in database.

    :param title: title given to the provided data
    :param data: the actual event data to be processed
    """

    # Create a unique constraint for instance and event IDs:
    run_query(queries.create_instance_constraint)

    stored_impacts = {}

    # Used for keeping track which processes, instances, initiators, events, adaptations have already been stored
    stored = {
        "processes": {},
        "instances": {},
        "initiators": {},
        "events": {},
        "adaptations": {},
    }

    # Dictionary for storing filename and data of file that contains total impact:
    impact_data_files = {}

    # Record event data along with overall impact of istances if they are given:
    print ("Recording in progress")
    process_event_data_helper_func(data, impact_data_files, 0, stored)
    record_impacts_helper_function(impact_data_files, stored_impacts)


def impact_from_api(data):
    """
    Function reads JSON data given by HTTP PUT request, where the data contains the overall impact(s) 
    of existing instances.

    :param title: name given to data
    :param data: actual impact data to be processed
    """

    # local dictionary to keep track of the single run's impacts:
    stored_impacts = {}

    # loop through every impact and record it in database:
    for case in data:
        add_impact_to_database(case, stored_impacts)
