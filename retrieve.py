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

def all_initiators_adaptations(tx):
    result = tx.run("""
        MATCH (initiator:Initiator)-[:INVOKES]->(adaptation:Adaptation)
        RETURN labels(initiator) AS initiator_labels, properties(initiator) AS initiator_properties,
               COLLECT(properties(adaptation)) AS adaptations
    """)
    return [record.data() for record in result]

def all_processes_instances(tx):
    result = tx.run("""
        MATCH (instance:Instance)-[:INSTANCE_OF]->(process:Process)
        RETURN labels(process) AS process_labels, properties(process) AS process_properties,
               COLLECT(properties(instance)) AS instance_properties
    """)
    return [record.data() for record in result]

def all_instances_events(tx):
    result = tx.run("""
        MATCH (event:Event)-[:STEP_OF]->(instance:Instance)
        RETURN labels(instance) AS instance_labels, properties(instance) AS instance_properties,
               COLLECT(properties(event)) AS event_properties
    """)


#This function retrieves the entire contents of the database
#It writes the contents to one JSON file
def retrieve_all():
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        to_json = session.execute_read(match_all)
        with open("database_contents.json", "w") as outfile:
            json.dump(to_json, outfile, indent=4)

    driver.close()

def retrieve_pre_made():
    print("Available queries:\n")
    print("1 - Retrieve all initiators and show which adaptations were invoked by each of them\n")
    print("2 - Show all processes and the instances of each of these processes\n")
    print("3 - Show all instances and all events in each of those instances\n")
    choice = int(input())
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        match choice:
            case 1:
                to_json = session.execute_read(all_initiators_adaptations)
                with open("query1.json", "w") as outfile:
                    json.dump(to_json, outfile, indent=4)
            case 2:
                to_json = session.execute_read(all_processes_instances)
                with open("query1.json", "w") as outfile:
                    json.dump(to_json, outfile, indent=4)
            case 3:
                to_json = session.execute_read(all_instances_events)
                with open("query1.json", "w") as outfile:
                    json.dump(to_json, outfile, indent=4)
            case _:
                print("Please double-check your input")

    driver.close()


def use_case():
    print("Choose your preferred use case for the retrieve method:\n")
    print("1 - retrieve all contents from the database\n")
    print("2 - retrieve contents based on a pre-made query\n")
    print("3 - retrieve contents based on a query of your choice\n")
    choice = int(input())
    match choice:
        case 1:
            retrieve_all()
        case 2:
            retrieve_pre_made()
        case _:
            print("Are you sure you have chosen a number 1-3?\n")


if __name__ == "__main__":
    use_case()