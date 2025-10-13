#The retrieve method should do three things:
#1)Return everything that is in the database and write it in a JSON file
#2)Give results of 1 or 2 pre-made boolean queries
#3)Allow the user to give some queries, and then retrieve from the database

from neo4j import GraphDatabase
import json

uri = "bolt://localhost:7687"
auth = ("neo4j", "internship123")

#The retrieval is to be done this way:
#Select all nodes, give the label, the properties of this and the connected node, also the relationship info
def match_all(tx):
    result = tx.run("""
        MATCH (node1)<-[relationship]-(node2)
        RETURN labels(node1) AS this_node_labels, properties(node1) AS this_node_properties,
               labels(node2) AS connected_node_labels,
               type(relationship) AS relationship_type, properties(relationship) AS relationship_properties
        
    """)

    #Return the result as a dictionary
    return [record.data() for record in result]

def direct_neighbors_query(tx, name1, name2):
    result = tx.run(f"""
        MATCH (n1:{name1})-[r]-(n2:{name2})
        RETURN labels(n1) AS node1_labels, properties(n1) AS node1_properties,
               COLLECT(properties(n2)) AS collect,
               type(r) as relationship
    """)

    return [record.data() for record in result]

#This function retrieves the entire contents of the database
#It writes the contents to one JSON file
def retrieve_all():
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        to_json = session.execute_read(match_all)
        with open("database_contents.json", "w") as outfile:
            json.dump(to_json, outfile, indent=4)

    driver.close()

def direct_neighbors():
    node1 = input("The first node:")
    node2 = input("The second node (the collect will be performed on this one):")
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        to_json = session.execute_read(direct_neighbors_query, node1.capitalize(), node2.capitalize())
        with open("query1.json", "w") as outfile:
            json.dump(to_json, outfile, indent=4)

    driver.close()


def use_case():
    print("Choose your preferred use case for the retrieve method:\n")
    print("1 - retrieve all contents from the database\n")
    print("2 - retrieve nodes and their direct neighbors using COLLECT\n")
    print("3 - retrieve contents based on a query of your choice\n")
    choice = int(input())
    match choice:
        case 1:
            retrieve_all()
        case 2:
            direct_neighbors()
        case _:
            print("Are you sure you have chosen a number 1-3?\n")


if __name__ == "__main__":
    use_case()