"""
This file contains all functions holding the queries to be executed.
"""


def match_all(tx):
    result = tx.run("""
        MATCH (node1)<-[relationship]-(node2)
        RETURN labels(node1) AS this_node_labels, properties(node1) AS this_node_properties,
               labels(node2) AS connected_node_labels,
               type(relationship) AS relationship_type, properties(relationship) AS relationship_properties
    """)

    # Return the result as a dictionary
    return [record.data() for record in result]

def direct_neighbors_collect_query(tx, name1, name2):
    result = tx.run(f"""
        MATCH (n1:{name1})-[r]-(n2:{name2})
        RETURN labels(n1) AS node1_labels, properties(n1) AS node1_properties,
               COLLECT(properties(n2)) AS collect,
               type(r) as relationship
    """)
    return [record.data() for record in result]

def direct_neighbors_count_query(tx, name1, name2):
    result = tx.run(f"""
        MATCH (n1:{name1})-[r]-(n2:{name2})
        RETURN labels(n1) AS node1_labels,
               COUNT(COLLECT(n2)) AS count
    """)

    return [record.data() for record in result]

def count_all_nodes_query(tx):
    result = tx.run(f"""
        MATCH (n)
        RETURN COUNT(n) AS NumberOfAllNodes
    """)

    return [record.data() for record in result]

def count_nodes_label_query(tx, label):
    result = tx.run(f"""
        MATCH (node:{label})
        RETURN count(node) AS NrNodes
    """)
    return [record.data() for record in result]

def count_property_query(tx, label, node_property, property_value):
    result = tx.run(f"""
        MATCH (node: {label})
        WHERE node.{node_property} = $property_value
        RETURN COUNT(node) AS NrNodes, labels(node) as NodeLabels
    """, property_value=property_value)
    return [record.data() for record in result]

def nodes_property_value_query(tx, label, node_property, property_value):
    result = tx.run(f"""
        MATCH (node: {label})
        WHERE node.{node_property} = $property_value
        RETURN labels(node) as NodeLabels
    """, property_value=property_value)
    return [record.data() for record in result]

def min_max_count_dir_neighbors(tx, label1, label2, func):
    result = tx.run(f"""
        MATCH (node1:{label1})-[r]-(node2:{label2})
        WITH node1, COUNT(DISTINCT node2) AS neighbor_count
        RETURN {func}(neighbor_count) AS {func}_neighbor_count, labels(node1) AS node1_labels,
        labels(node2) AS node2_labels
    """)
    return [record.data() for record in result]

def two_node_relationship_query(tx, label1, label2):
    result = tx.run(f"""
        MATCH (node1:{label1})-[r]-(node2:{label2})
        RETURN type(r), properties(r)
    """)
    return [record.data() for record in result]


def property_keys_query(tx, label):
    result = tx.run(f"""
        MATCH (node:{label})
        UNWIND keys(node) AS property_keys
        RETURN DISTINCT property_keys
    """)
    return [record.data() for record in result]


def all_labels_query(tx):
    result = tx.run(f"""
        MATCH (n)
        RETURN DISTINCT labels(n) AS labels
    """)
    return [record.data() for record in result]


def all_relationships_query(tx):
    result = tx.run(f"""
        MATCH (n)-[r]-(n2)
        RETURN DISTINCT type(r) AS relationship_type
    """)
    return [record.data() for record in result]

def disconnected_nodes_query(tx):
    result = tx.run(f"""
        MATCH (n)
        WHERE size((n)--()) = 0
        RETURN labels(n), properties(n)
    """)
    return [record.data() for record in result]