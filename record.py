import json
import os
from neo4j import GraphDatabase
import re

from model.Event import Event
from model.Instance import Instance
from model.Process import Process
from model.Adaptation import Adaptation

uri = "bolt://localhost:7687"
auth = ("neo4j", "internship123")

def create_process(tx, id_num):
    tx.run("CREATE (:Process {id: $id_number})", id_number=id_num)

def create_event(tx, name, time, resource):
    tx.run("CREATE (:Event {name: $name, time: $time, resource: $resource})", name=name, time=time, resource=resource)

def create_adaptation(tx, ad_type, time, change):
    tx.run("CREATE (:Adaptation {type: $adaptation_type, time: $time, change: $change})", adaptation_type=ad_type, time=time, change=change)


def record(json_dir):
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        #Go through every subdirectory of the directory of the JSON files
        for path, folders, files in os.walk(json_dir):
            #Go through all files in the file list
            for file in files:
                #Merge the directory with the file name
                file_path = os.path.join(path, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    #Load the data from the JSON file
                    data = json.load(f)

                #Instanitate the process, the process ID for now is the name of the file
                file_name = file.replace(".json", "")
                process = Process(file_name)
                session.execute_write(create_process, process.id_number)

                for case in data:

                    #Loop through all events
                    for e in case["events"]:
                        #Event has properties name, time, resource
                        #Get these properties and create an event object
                        event = Event(e.get("concept:name", ""), e.get("time:timestamp", ""), e.get("org:resource", ""))
                        #Create the node of the event in the database
                        session.execute_write(create_event, event.name, event.time, event.resource)

                        #I try to find any label that starts with 'adaptation'
                        #'.' means any character, '*' means 0 or more occurrences
                        if any(re.search(r"adaptation:.*", key) for key in e.keys()):
                            adaptation = Adaptation(e["adaptation:type"], e.get("adaptation:timestamp", ""), e.get("adaptation:change", ""))

                            session.execute_write(create_adaptation, adaptation.adaptation_type, adaptation.time, adaptation.change)



    driver.close()


if __name__ == "__main__":
    record("./json_files")