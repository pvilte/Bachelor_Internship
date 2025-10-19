import datetime
from neo4j import GraphDatabase
import json
from . import queries
from datetime import datetime
from neo4j.time import DateTime

# Change the values here based on your environment
uri = "bolt://127.0.0.1:7687"
auth = ("neo4j", "internship123")

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

    with open("result.json", "w") as outfile:
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
        "Adaptation": ["time", "type", "change"],
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


def direct_neighbors_collect():
    """
    This function calls the query function to retrieve all direct neighbors collected on a label
    and calls the function to write the result to a JSON file
    """
    while True:
        node1 = str(input("The first node: ")).capitalize()
        node2 = str(input("The second node (the collect will be performed on this one): ")).capitalize()
        if label_check(node1) and label_check(node2):
            write_json(run_query(queries.direct_neighbors_collect_query, node1, node2))
            break


def count_direct_neighbors():
    """
    This function calls function to retrieve the number of all direct neighbors collected on a certain label,
    then calls function to write the result to a JSON file
    """
    while True:
        node1 = str(input("The first node: ")).capitalize()
        node2 = str(input("The second node (nodes of this label will be counted): ")).capitalize()
        if label_check(node1) and label_check(node2):
            write_json(run_query(queries.direct_neighbors_count_query, node1, node2))
            break


def count_all_nodes():
    """
    This function calls the function to count the number of all nodes in the database,
    then calls the function to write the result to a JSON file
    """
    write_json(run_query(queries.count_all_nodes_query))


def count_nodes_label():
    """
    This function calls the function to count the number of nodes in the database with the provided label,
    then calls the function to write the result to a JSON file
    """
    while True:
        node = str(input("Label: ")).capitalize()
        if label_check(node):
            write_json(run_query(queries.count_nodes_label_query, node))
            break


def count_based_on_property_value():
    """
    This function calls the function to count the number of nodes based on a specific label and a specific property value,
    then calls the function to write the result to a JSON file
    """
    while True:
        node = str(input("Label: ")).capitalize()
        node_property = str(input("Property: ")).lower()
        property_value = str(input("Value: "))
        property_value = time_conversion(property_value, node_property)
        if label_check(node) and property_check(node, node_property):
            write_json(run_query(queries.count_property_query, node, node_property, property_value))
            break


def nodes_property_value():
    """
    This function calls a function to retrieve all nodes based on a label and a specific property value,
    and then calls the function to write the result to a JSON file
    """
    while True:
        node = str(input("Label: ")).capitalize()
        node_property = str(input("Property: ")).lower()
        property_value = str(input("Value: "))
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


def choose_count_application():
    """
    This function allows the user to choose which count application to use
    """
    print("1 - count all nodes in the database\n")
    print("2 - count the direct neighbors of a node\n")
    print("3 - count all nodes of a specific label\n")
    print("4 - count nodes based on a property value\n")
    print("5 - count all relationships in the database\n")
    choice = int(input("Your choice: "))
    match choice:
        case 1:
            count_all_nodes()
        case 2:
            count_direct_neighbors()
        case 3:
            count_nodes_label()
        case 4:
            count_based_on_property_value()
        case 5:
            count_all_relationships()
        case _:
            print("Please enter a valid choice!\n")

def two_node_relationships():
    """
    This function calls the function to retrieve the relationship between two nodes,
    then calls the function to write the result to a JSON file
    """
    while True:
        node1 = str(input("The first node: ")).capitalize()
        node2 = str(input("The second node: ")).capitalize()
        if label_check(node1) and label_check(node2):
            write_json(run_query(queries.two_node_relationship_query, node1, node2))
            break


def property_keys():
    """
    This function calls the query function that, given the label, retrieves the property keys,
    then calls the function to write the result to a JSON file
    """
    while True:
        node = str(input("Label: ")).capitalize()
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

def most_incoming_relationships_to_nodes():
    """
    This function calls the function to retrieve the node based on a label of most incoming relationships in the database,
    then calls the function to write the result to a JSON file
    """
    while True:
        label = input("Label: ").capitalize()
        if label_check(label):
            write_json(run_query(queries.most_incoming_relationships_to_nodes_query, label))
            break

def use_case():
    """
    This function allows the user how to approach the retrieval
    """
    print("Choose your preferred use case for the retrieve method:\n")
    print("1 - retrieve all contents from the database\n")
    print("2 - retrieve nodes and their direct neighbors using COLLECT\n")
    print("3 - retrieve contents based on count\n")
    print("4 - retrieve contents based on property value\n")
    print("5 - retrieve relationships between two nodes\n")
    print("6 - retrieve all property keys for a label of a node\n")
    print("7 - retrieve all labels of nodes that exist in the database\n")
    print("8 - retrieve all relationship types in the database\n")
    print("9 - retrieve any disconnected nodes\n")
    print("10 - retrieve the node with the most incoming relationships based on a label\n")
    choice = int(input("Your choice: "))
    match choice:
        case 1:
            retrieve_all()
        case 2:
            direct_neighbors_collect()
        case 3:
            choose_count_application()
        case 4:
            nodes_property_value()
        case 5:
            two_node_relationships()
        case 6:
            property_keys()
        case 7:
            all_labels()
        case 8:
            all_relationships()
        case 9:
            disconnected_nodes()
        case 10:
            most_incoming_relationships_to_nodes()
        case _:
            print("Are you sure you have chosen a number 1-3?\n")


if __name__ == "__main__":
    use_case()