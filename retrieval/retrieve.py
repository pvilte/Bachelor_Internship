from neo4j import GraphDatabase
import json
from . import queries

uri = "bolt://localhost:7687"
auth = ("neo4j", "internship123")

#Function for running the queries
def run_query(query_func, *args):
    driver = GraphDatabase.driver(uri=uri, auth=auth)
    with driver.session() as session:
        result = session.execute_read(query_func, *args)
    driver.close()
    return result

#Function for writing the result to a JSON file
def write_json(to_json):
    with open("query1.json", "w") as outfile:
        json.dump(to_json, outfile, indent=4)

#Safety check function to see if the given node really has the property
def property_check(node, node_property):
    if not hasattr(node, node_property):
        print("Are you sure you have spelled the property correctly?")
        return False

    return True

#Safety check to see if the given label of the node really exists
def label_check(node):
    model_list = ["Adaptation", "Event", "Initiator", "Instance", "Process"]
    if node in model_list:
        return True
    else:
        print("Are you sure you have spelled the label correctly?")
        return False


#This function retrieves the entire contents of the database
def retrieve_all():
    write_json(run_query(queries.match_all))


def direct_neighbors_collect():
    while True:
        node1 = str(input("The first node:"))
        node2 = str(input("The second node (the collect will be performed on this one):"))
        if label_check(node1) and label_check(node2):
            write_json(run_query(queries.direct_neighbors_collect_query, node1.capitalize(), node2.capitalize()))
            break


def count_direct_neighbors():
    while True:
        node1 = str(input("The first node:"))
        node2 = str(input("The second node (the collect will be performed on this one):"))
        if label_check(node1) and label_check(node2):
            write_json(run_query(queries.direct_neighbors_count_query, node1.capitalize(), node2.capitalize()))
            break


def count_all_nodes():
    write_json(run_query(queries.count_all_nodes_query))


def count_nodes_label():
    while True:
        node = str(input("Label: "))
        if label_check(node):
            write_json(run_query(queries.count_nodes_label_query, node))
            break


def count_based_on_property_value():
    while True:
        node = str(input("Label: ")).capitalize()
        node_property = str(input("Property: ")).lower()
        property_value = str(input("Value: "))

        if label_check(node) and property_check(node, node_property):
            write_json(run_query(queries.count_property_query, node, node_property, property_value))
            break


def max_min_count():
    while True:
        node1 = str(input("The first node: ")).capitalize()
        node2 = str(input("The second node: ")).capitalize()
        function = str(input("MIN or MAX: ")).upper()
        if not function == "MIN" or not function == "MAX":
            print("Enter MIN or MAX!\n")
        if label_check(node1) and label_check(node2):
            write_json(run_query(queries.min_max_count_dir_neighbors, node1, node2, function.capitalize()))
            break


def nodes_property_value():
    while True:
        node = str(input("Label: ")).capitalize()
        node_property = str(input("Property: ")).lower()
        property_value = str(input("Value: "))
        if label_check(node) and property_check(node, node_property):
            write_json(run_query(queries.nodes_property_value_query, node, node_property, property_value))
            break



def choose_count_application():
    print("1 - count all nodes in the database\n")
    print("2 - count the direct neighbors of a node\n")
    print("3 - count all nodes of a specific label\n")
    print("4 - count nodes based on a property value\n")
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
        case _:
            print("Please enter a valid choice!\n")

def two_node_relationships():
    while True:
        node1 = str(input("The first node: ")).capitalize()
        node2 = str(input("The second node: ")).capitalize()
        if label_check(node1) and label_check(node2):
            write_json(run_query(queries.two_node_relationship_query, node1, node2))
            break


def property_keys():
    while True:
        node = str(input("Label: ")).capitalize()
        if label_check(node):
            write_json(run_query(queries.property_keys_query, node))
            break

def all_labels():
    write_json(run_query(queries.all_labels_query))

def all_relationships():
    write_json(run_query(queries.all_relationships_query))

def disconnected_nodes():
    write_json(run_query(queries.disconnected_nodes_query))

def use_case():
    print("Choose your preferred use case for the retrieve method:\n")
    print("1 - retrieve all contents from the database\n")
    print("2 - retrieve nodes and their direct neighbors using COLLECT\n")
    print("3 - retrieve contents based on count\n")
    print("4 - retrieve contents based on minimum/maximum\n")
    print("5 - retrieve contents based on property value\n")
    print("6 - retrieve relationships between two nodes\n")
    print("7 - retrieve all property keys for a label of a node\n")
    print("8 - retrieve all labels of nodes that exist in the database\n")
    print("9 - retrieve all relationship types in the database\n")
    print("10 - retrieve any disconnected nodes\n")
    choice = int(input("Your choice: "))
    match choice:
        case 1:
            retrieve_all()
        case 2:
            direct_neighbors_collect()
        case 3:
            choose_count_application()
        case 4:
            max_min_count()
        case 5:
            nodes_property_value()
        case 6:
            two_node_relationships()
        case 7:
            property_keys()
        case 8:
            all_labels()
        case 9:
            all_relationships()
        case 10:
            disconnected_nodes()
        case _:
            print("Are you sure you have chosen a number 1-3?\n")


if __name__ == "__main__":
    use_case()