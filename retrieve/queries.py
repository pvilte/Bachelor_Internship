"""
This file contains all functions with queries to be executed by the retrieve.py file
Each function receives tx transaction object because all queries must be executed in that transaction
All the functions below returns a dictionary
"""


def match_all(tx):
    """
    For every node, return all nodes it is connected to, the labels, properties and relationship types
    """

    query = """
        MATCH (node1)-[relationship]-(node2)
        RETURN labels(node1) AS this_node_labels, properties(node1) AS this_node_properties,
               labels(node2) AS connected_node_labels, properties(node2) AS connected_node_properties,
               type(relationship) AS relationship_type
    """

    result = tx.run(query)

    # Display the query used to the user:
    print("Query used to retrieve all contents from the database:")
    print(query)

    return [record.data() for record in result]


def events_with_adaptations(tx):
    """
    This returns the events that have adaptations linked to them.
    """

    query = """
        MATCH (:Adaptation)-[:APPLIED_TO]->(event:Event)
        RETURN DISTINCT event
    """

    result = tx.run(query)

    # Display the query used to the user:
    print("Query used to retrieve all events with adaptations:")
    print(query)

    return [record.data() for record in result]


def adaptation_of_event(tx, event_id):
    """
    This returns the adaptation of a provided event.

    :param event_id: the id of the event the user selected
    """

    query = f"""
        MATCH (a:Adaptation)-[:APPLIED_TO]->(e:Event)
        WHERE e.id = "{event_id}"
        RETURN a
    """

    result = tx.run(query)

    # Display the query used to the user:
    print("Query used to retrieve selected event's adaptation:")
    print(query)

    return [result.data()]


def direct_neighbors_collect_query(tx, name1, name2):
    """
    Retrieves collected direct neighbors of node1, giving properties, labels and relationships of the nodes

    :param name1: label of the first node
    :param name2: label of the second node
    """

    query = f"""
        MATCH (n1:{name1})-[r]-(n2:{name2})
        RETURN labels(n1) AS node1_labels, properties(n1) AS node1_properties,
               COLLECT(properties(n2)) AS collect_properties, COLLECT(DISTINCT labels(n2)) AS collect_labels, 
               type(r) as relationship
    """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve direct neighbours of {name1}:")
    print(query)

    return [record.data() for record in result]


def direct_neighbors_count_query(tx, name1, name2):
    """
    This function retrieves the labels and properties of node1 and node2,
     counts the collected direct neighbors on node2

     :param name1: label of the first node
     :param name2: label of the second node
    """

    query = f"""
        MATCH (n1:{name1})-[r]-(n2:{name2})
        RETURN properties(n1) AS node1_properties,
               labels(n1) AS node1_labels,
               COUNT(DISTINCT n2) AS neighbor_count,
               COLLECT(DISTINCT properties(n2)) AS neighbor_properties,
               COLLECT(DISTINCT labels(n2)) AS neighbor_labels
    """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve the count of direct neighbours of {name2}:")
    print(query)

    return [record.data() for record in result]


def count_all_nodes_query(tx):
    """
    This function counts how many nodes there are in the entire database
    """

    query = f"""
        MATCH (n)
        RETURN COUNT(n) AS NumberOfAllNodes
    """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve count of all nodes:")
    print(query)

    return [record.data() for record in result]

def count_nodes_label_query(tx, label):
    """
    This function counts the number of nodes with the given label

    :param label: label of the node
    """

    query = f"""
        MATCH (node:{label})
        RETURN COUNT(node) AS NrNodes
    """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve the count nodes of {label} label:")
    print(query)

    return [record.data() for record in result]

def count_property_query(tx, label, node_property, property_value):
    """
    This function counts the number of nodes with the given label and the given property value, returns the number
    and the labels of the node

    :param label: label of the node
    :param node_property: property key of the node
    :param property_value: value of the property
    """

    # If node_property is time, print the unmodified time value:
    if node_property == "time":
        time_property_val = str(property_value).replace(" ", "T", 1)
        print_property_val = f'datetime("{time_property_val}")'
    else:
        print_property_val = f'"{property_value}"'

    query = f"""MATCH (node: {label})
        WHERE node.{node_property} = {print_property_val}
        RETURN COUNT(node) AS NrNodes, labels(node) as NodeLabels
    """

    result = tx.run(f"""
        MATCH (node: {label})
        WHERE node.{node_property} = $property_value
        RETURN COUNT(node) AS NrNodes, labels(node) as NodeLabels
    """, property_value=property_value)

    # Display the query used to the user:
    print(f"Query used to retrieve the count nodes with given label: {label}, and property value: {property_value}:")
    print(query)

    return [record.data() for record in result]

def nodes_property_value_query(tx, label, node_property, property_value):
    """
    This function retrieves the labels and properties of nodes with the given property value

    :param label: label of the node
    :param node_property: property key of the node
    :param property_value: value of the property
    """

    # If node_property is time, print the unmodified time value in date:
    if node_property == "time":
        time_property_val = str(property_value).replace(" ", "T", 1)
        print_property_val = f'datetime("{time_property_val}")'
    else:
        print_property_val = f'"{property_value}"'
    
    query = f"""
        MATCH (node: {label})
        WHERE node.{node_property} = {print_property_val}
        RETURN labels(node) as NodeLabels, properties(node) as NodeProperties
    """

    result = tx.run(f"""
        MATCH (node: {label})
        WHERE node.{node_property} = $property_value
        RETURN labels(node) as NodeLabels, properties(node) as NodeProperties
    """, property_value=property_value)
    
    # Display the query used to the user:
    print(f"Query used to retrieve nodes with given label: {label}, and property value: {property_value}:")
    print(query)
    
    return [record.data() for record in result]

def two_node_relationship_query(tx, label1, label2):
    """
    This function retrieves distinct relationship type of the given two nodes

    :param label1: label of the first node
    :param label2: label of the second node
    """

    query = f"""
        MATCH (node1:{label1})-[r]-(node2:{label2})
        RETURN DISTINCT type(r) AS relationship_type
    """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve relationship type of {label1} and {label2}:")
    print(query)

    return [record.data() for record in result]


def property_keys_query(tx, label):
    """
    This function retrieves the property keys of the given label

    :param label: label of the node
    """

    query = f"""
        MATCH (node:{label})
        UNWIND keys(node) AS property_keys
        RETURN DISTINCT property_keys
    """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve property keys of {label}:")
    print(query)

    return [record.data() for record in result]


def all_labels_query(tx):
    """
    This function retrieves the labels of all nodes
    """

    query = f"""
        MATCH (n)
        RETURN DISTINCT labels(n) AS labels
    """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve labels of all nodes:")
    print(query)
    
    return [record.data() for record in result]


def all_relationships_query(tx):
    """
    This function retrieves all relationship types in the database
    """

    query = f"""
        MATCH (n)-[r]-(n2)
        RETURN DISTINCT type(r) AS relationship_type
    """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve all relationship types:")
    print(query)
    
    return [record.data() for record in result]

def disconnected_nodes_query(tx):
    """
    This function retrieves labels and properties of the disconnected nodes
    """

    query = f"""
        MATCH (n)
        WHERE NOT EXISTS((n)--())
        RETURN labels(n), properties(n)
    """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve labels annd properties of disconnected nodes:")
    print(query)

    return [record.data() for record in result]

def most_incoming_relationships_to_nodes_query(tx, label):
    """
    This function retrieves labels and properties of the node of the given label
    that has the most incoming relationships

    :param label: label of the node
    """

    query = f"""
        MATCH (n1:{label})<-[r]-(n2)
        RETURN labels(n1) as labels,
               properties(n1) as properties,
               COUNT (DISTINCT n2) as nodes_connected_by_relationship
        ORDER BY nodes_connected_by_relationship DESC
        LIMIT 1
        """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve labels and properties of nodes given {label} that has the most incomming relationships:")
    print(query)

    return [record.data() for record in result]

def count_all_relationships_query(tx):
    """
    This function retrieves the count of all relationships in the database
    """

    query = f"""
        MATCH (n1)-[r]-(n2)
        RETURN COUNT (DISTINCT r) AS NrRelationships
    """

    result = tx.run(query)

    # Display the query used to the user:
    print(f"Query used to retrieve the count of all relationships:")
    print(query)

    return [record.data() for record in result]
