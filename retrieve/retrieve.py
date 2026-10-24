import datetime
from neo4j import GraphDatabase
import json
from . import queries
from datetime import datetime
from neo4j.time import DateTime
import os

uri = os.getenv("NEO4J_URI")
auth = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

def run_query(query_func, *args):
    """
    This function creates a connection to a neo4j database, creates a session, and executes a read query.
    Then, the driver is closed to release any resources still held by it.

    :param query_func: the function to execute; these functions reside in queries.py directory
    :param args: unfixed number of arguments to be given to the query function
    :return: string to be written to JSON
    """
    driver = GraphDatabase.driver(uri=uri, auth=auth)
    with driver.session() as session:
        result = session.execute_read(query_func, *args)
    driver.close()
    return result

def convert_neo4j_to_json(data):
    """
    This function converts Neo4j data types to JSON types

    :param data: Neo4j data types to be converted
    :return: string to be written to JSON
    """
    if isinstance(data, (DateTime, datetime)):
        return data.isoformat()
    elif isinstance(data, list):
        return [convert_neo4j_to_json(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_neo4j_to_json(value) for key, value in data.items()}
    else:
        return data

def write_json(to_json):
    """
    This function writes the given JSON string to file 'result.json'

    :param to_json: the string to be written to file
    :return: void
    """

    with open("/app/output/result.json", "w") as outfile:
        json.dump(convert_neo4j_to_json(to_json), outfile, indent=4)

def time_conversion(property_value, property_key):
    """
    If the given property key is "time", then the datatype of property value should be adjusted accordingly

    :param property_value: the property value to be adjusted
    :param property_key: the key of the property to be checked
    :return: the adjusted property value based on the datatype
    """
    if property_key == "time":
        try:
            property_value = datetime.fromisoformat(property_value)
        except:
            return property_value

    return property_value

def property_check(node, node_property):
    """
    This function checks if the given label of a node has the property.

    :param node: the label of a node to be checked
    :param node_property: the property to be checked
    """

    properties = {
        "Adaptation": ["time", "type", "change", "reason", "impact"],
        "Event": ["time", "name", "resource"],
        "Initiator": ["name"],
        "Instance": ["id"],
        "Process": ["id"]
    }
    if node in properties and node_property in properties[node]:
        return True
    else:
        print("Are you sure you have spelled the property correctly?")
        return False


def label_check(node):
    """
    This function checks if the node label given by the user has one of the supported names

    :param node: the node to be checked
    """

    model_list = ["Adaptation", "Event", "Initiator", "Instance", "Process"]
    if node in model_list:
        return True
    else:
        print("Are you sure you have spelled the labels correctly?")
        return False


def retrieve_all():
    """
    This function calls the query function to retrieve all contents from the database and calls the function
    to write the result to a JSON file
    """
    write_json(run_query(queries.match_all))


def direct_neighbors_collect(node1: str, node2: str):
    """
    This function calls the query function to retrieve all direct neighbors collected on a label
    and calls the function to write the result to a JSON file
    """
    while True:
        node1 = node1.capitalize()
        node2 = node2.capitalize()
        if label_check(node1) and label_check(node2):
            write_json(run_query(queries.direct_neighbors_collect_query, node1, node2))
            break


def count_direct_neighbors(node1: str, node2: str):
    """
    This function calls function to retrieve the number of all direct neighbors collected on a certain label,
    then calls function to write the result to a JSON file
    """
    while True:
        node1 = node1.capitalize()
        node2 = node2.capitalize()
        if label_check(node1) and label_check(node2):
            write_json(run_query(queries.direct_neighbors_count_query, node1, node2))
            break


def count_all_nodes():
    """
    This function calls the function to count the number of all nodes in the database,
    then calls the function to write the result to a JSON file
    """
    write_json(run_query(queries.count_all_nodes_query))


def count_nodes_label(node: str):
    """
    This function calls the function to count the number of nodes in the database with the provided label,
    then calls the function to write the result to a JSON file
    """
    while True:
        node = node.capitalize()
        if label_check(node):
            write_json(run_query(queries.count_nodes_label_query, node))
            break


def count_based_on_property_value(node: str, node_property: str, property_value: str):
    """
    This function calls the function to count the number of nodes based on a specific label and a specific property value,
    then calls the function to write the result to a JSON file
    """
    while True:
        node = node.capitalize()
        node_property = node_property.lower()
        property_value = time_conversion(property_value, node_property)
        if label_check(node) and property_check(node, node_property):
            write_json(run_query(queries.count_property_query, node, node_property, property_value))
            break


def nodes_property_value(node: str, node_property: str, property_value: str):
    """
    This function calls a function to retrieve all nodes based on a label and a specific property value,
    and then calls the function to write the result to a JSON file
    """
    while True:
        node = node.capitalize()
        node_property = node_property.lower()
        property_value = time_conversion(property_value, node_property)
        if label_check(node) and property_check(node, node_property):
            write_json(run_query(queries.nodes_property_value_query, node, node_property, property_value))
            break

def count_all_relationships():
    """
    This function calls the function to count the number of all relationships in the database,
    then calls the function to write the result to a JSON file
    """
    write_json(run_query(queries.count_all_relationships_query))


def two_node_relationships(node1: str, node2: str):
    """
    This function calls the function to retrieve the relationship between two nodes,
    then calls the function to write the result to a JSON file
    """
    while True:
        node1 = node1.capitalize()
        node2 = node2.capitalize()
        if label_check(node1) and label_check(node2):
            write_json(run_query(queries.two_node_relationship_query, node1, node2))
            break


def property_keys(node: str):
    """
    This function calls the query function that, given the label, retrieves the property keys,
    then calls the function to write the result to a JSON file
    """
    while True:
        node = node.capitalize()
        if label_check(node):
            write_json(run_query(queries.property_keys_query, node))
            break

def all_labels():
    """
    This function calls the function to retrieve all labels in the database,
    then calls the function to write the result to a JSON file
    """
    write_json(run_query(queries.all_labels_query))

def all_relationships():
    """
    This function calls the function to retrieve all relationships in the database,
    then calls the function to write the result to a JSON file
    """
    write_json(run_query(queries.all_relationships_query))

def disconnected_nodes():
    """
    This function calls the function to retrieve all disconnected nodes in the database,
    then calls the function to write the result to a JSON file
    """
    write_json(run_query(queries.disconnected_nodes_query))

def most_incoming_relationships_to_nodes(label: str):
    """
    This function calls the function to retrieve the node based on a label of most incoming relationships in the database,
    then calls the function to write the result to a JSON file
    """
    while True:
        label = label.capitalize()
        if label_check(label):
            write_json(run_query(queries.most_incoming_relationships_to_nodes_query, label))
            break


def all_events_with_adaptations():
    """
    This function returns collects all events that have adaptations and writes result to a JSON file.
    """

    # Save result so API can get the JSON response
    result = convert_neo4j_to_json(run_query(queries.events_with_adaptations))
    # Write to result.json
    write_json(result)
    return result


def adaptations_of_events():
    """
    This function asks user to select an available event with an adaptation and based on that input
    retrieves the adaptation.
    """

    events_with_adapt = run_query(queries.events_with_adaptations_list)


    adaptations = {}
    for event in events_with_adapt:
        chosen_event_id = event["event"]["id"]
        adaptation = run_query(queries.adaptation_of_event, chosen_event_id)
        adaptations[chosen_event_id] = adaptation

    return adaptations


def reason_and_impact_keys_of_adaptation(key: str):
    """
    This function calls the query functions, that given the label, returns reason, impact
    key values of an adaptation. Then it calls the function to write the result to a JSON file
    """
    adaptations = adaptations_of_events()

    result= {}

    key = key.strip().lower()

    for event_id, adapt in adaptations.items():
        if key == "reason":
            reason = adapt[0][0]["a"]["reason"]
            # check if the field is empty and skip it if it is:
            if reason == "":
                continue
            result[event_id] = [{"reason": reason}]

        elif key == "impact":
            impact = adapt[0][0]["a"]["impact"]
            # check if the field is empty and skip it if it is:
            if impact == "":
                continue
            result[event_id] = [{"impact": impact}]

        elif key == "both":
            reason = adapt[0][0]["a"]["reason"]
            impact = adapt[0][0]["a"]["impact"]
            # check if both fields are empty and skip them if they are:
            if reason == "" and impact == "":
                continue
            elif reason == "":
                result[event_id] = [{"impact": impact}]
            elif impact == "":
                result[event_id] = [{"reason": reason}]
            else:
                result[event_id] = [{"reason": reason}, {"impact": impact}]
        
        else:
            raise ValueError(f"the key '{key}' does not match one of the following: impact, reason, both.")
    
    write_json(result)
    return result


def collect_trace_based_on_trace_id(instance_id: str):
    """
    This function uses query to display an entire trace using an instance_id and writes result to JSON file.
    """

    instance_id = instance_id.strip()
    # Save result so API can get the JSON response
    result = convert_neo4j_to_json(run_query(queries.trace_based_on_instance_id, instance_id))
    # Write result to result.json
    write_json(result)
    return result


def collect_all_traces():
    """
    This function uses query to collect all available traces with the process_id, instance_id,
    as well as lists the events and their adaptations (if there are any), before writing result to a JSON file.
    """

    # Save result so API can get the JSON response
    result = convert_neo4j_to_json(run_query(queries.all_traces))
    # Write to result.json
    write_json(result)
    return result


def collect_impact_of_instance(instance_id: str):
    """
    This function uses query to collect the impact of a selected instance with the use of instance_id,
    before writing result to a JSON file.
    """

    instance_id = instance_id.strip()
    # Save result so API can get the JSON response
    result = convert_neo4j_to_json(run_query(queries.impact_of_instance, instance_id))
    # Write to result.json
    write_json(result)
    return result

