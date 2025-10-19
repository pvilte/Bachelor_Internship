"""
This file contains all functions with queries to be executed by the retrieve.py file
Each function receives tx transaction object because all queries must be executed in that transaction
All the functions below returns a dictionary
"""


def match_all(tx):
    """
    For every node, return all nodes it is connected to, the labels, properties and relationship types and properties
    """
    result = tx.run("""
        MATCH (node1)-[relationship]-(node2)
        RETURN labels(node1) AS this_node_labels, properties(node1) AS this_node_properties,
               labels(node2) AS connected_node_labels, properties(node2) AS connected_node_properties,
               type(relationship) AS relationship_type, properties(relationship) AS relationship_properties
    """)
    return [record.data() for record in result]

def direct_neighbors_collect_query(tx, name1, name2):
    """
    Retrieves collected direct neighbors of node1, giving properties, labels and relationships of the nodes
    """
    result = tx.run(f"""
        MATCH (n1:{name1})-[r]-(n2:{name2})
        RETURN labels(n1) AS node1_labels, properties(n1) AS node1_properties,
               COLLECT(properties(n2)) AS collect_properties, COLLECT(DISTINCT labels(n2)) AS collect_labels, 
               type(r) as relationship
    """)
    return [record.data() for record in result]

def direct_neighbors_count_query(tx, name1, name2):
    """
    This function retrieves the labels and properties of node1 and node2,
     counts the collected direct neighbors
    """
    result = tx.run(f"""
        MATCH (n1:{name1})-[r]-(n2:{name2})
        RETURN properties(n1) AS node1_properties,
               labels(n1) AS node1_labels,
               COUNT(DISTINCT n2) AS neighbor_count,
               COLLECT(DISTINCT properties(n2)) AS neighbor_properties,
               COLLECT(DISTINCT labels(n2)) AS neighbor_labels
    """)
    return [record.data() for record in result]

def count_all_nodes_query(tx):
    """
    This function counts how many nodes there are in the entire database
    """
    result = tx.run(f"""
        MATCH (n)
        RETURN COUNT(n) AS NumberOfAllNodes
    """)
    return [record.data() for record in result]

def count_nodes_label_query(tx, label):
    """
    This function counts the number of nodes with the given label
    """
    result = tx.run(f"""
        MATCH (node:{label})
        RETURN COUNT(node) AS NrNodes
    """)
    return [record.data() for record in result]

def count_property_query(tx, label, node_property, property_value):
    """
    This function counts the number of nodes with the given label and the given property value, returns the number
    and the labels of the node
    """
    result = tx.run(f"""
        MATCH (node: {label})
        WHERE node.{node_property} = $property_value
        RETURN COUNT(node) AS NrNodes, labels(node) as NodeLabels
    """, property_value=property_value)
    return [record.data() for record in result]

def nodes_property_value_query(tx, label, node_property, property_value):
    """
    This function retrieves the labels of nodes with the given property value
    """
    result = tx.run(f"""
        MATCH (node: {label})
        WHERE node.{node_property} = $property_value
        RETURN labels(node) as NodeLabels
    """, property_value=property_value)
    return [record.data() for record in result]

def two_node_relationship_query(tx, label1, label2):
    """
    This function retrieves distinct relationship type and the properties of the given two nodes
    """
    result = tx.run(f"""
        MATCH (node1:{label1})-[r]-(node2:{label2})
        RETURN DISTINCT type(r) AS relationship_type, properties(r) AS relationship_properties
    """)
    return [record.data() for record in result]


def property_keys_query(tx, label):
    """
    This function retrieves the property keys of the given label
    """
    result = tx.run(f"""
        MATCH (node:{label})
        UNWIND keys(node) AS property_keys
        RETURN DISTINCT property_keys
    """)
    return [record.data() for record in result]


def all_labels_query(tx):
    """
    This function retrieves the labels of all nodes
    """
    result = tx.run(f"""
        MATCH (n)
        RETURN DISTINCT labels(n) AS labels
    """)
    return [record.data() for record in result]


def all_relationships_query(tx):
    """
    This function retrieves all relationships in the database
    """
    result = tx.run(f"""
        MATCH (n)-[r]-(n2)
        RETURN DISTINCT type(r) AS relationship_type
    """)
    return [record.data() for record in result]

def disconnected_nodes_query(tx):
    """
    This function retrieves labels and properties of the disconnected nodes
    """
    result = tx.run(f"""
        MATCH (n)
        WHERE NOT EXISTS((n)--())
        RETURN labels(n), properties(n)
    """)
    return [record.data() for record in result]

def most_incoming_relationships_to_nodes_query(tx, label):
    result = tx.run(f"""
        MATCH (n1:{label})<-[r]-(n2)
        RETURN labels(n1) as labels,
               properties(n1) as properties,
               COUNT (DISTINCT n2) as nodes_connected_by_relationship
        ORDER BY nodes_connected_by_relationship DESC
        LIMIT 1
        """)
    return [record.data() for record in result]

def count_all_relationships_query(tx):
    result = tx.run(f"""
        MATCH (n1)-[r]-(n2)
        RETURN COUNT (DISTINCT r) AS NrRelationships
    """)
    return [record.data() for record in result]
