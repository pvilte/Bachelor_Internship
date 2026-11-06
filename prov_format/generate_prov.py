import prov.model as pm
from prov.dot import prov_to_dot
from pathlib import Path
from rdflib import Dataset
import json
import os

def create_delete_adaptation(document, adaptation, initiator):
    """
    Function creates a delete adaptation entity and links it to to initiator and event activity.

    :params document: ProvDocument to which the data is saved.
    :params adaptation: adaptation object
    :param initiator: adaptation initiator
    """

    # Create adaptation event activity:
    change_name = adaptation["change"]
    change_capitalized = change_name.title().replace(" ", "")
    delete_event = document.activity(f"ex:Adaptation{change_capitalized}", other_attributes={
        "prov:label": f"{adaptation['time']}",
    },)
    # Create an Adaptation entity:
    impact = adaptation["impact"]
    if impact == "":
        adapt_en = document.entity(f"ex:{adaptation['id']}", other_attributes={
            "ex:type": f"{adaptation['type']}",
            "ex:change": f"{adaptation['change']}",
        },)
    else:
        adapt_en = document.entity(f"ex:{adaptation['id']}", other_attributes={
            "ex:type": f"{adaptation['type']}",
            "ex:change": f"{adaptation['change']}",
            "ex:impact": f"{impact}",
        },)

    # Create attribution between initiator and entity:
    document.wasAttributedTo(adapt_en, initiator)

    # Create generation between entity and activity
    reason = adaptation["reason"]
    if reason == "":
        document.wasGeneratedBy(adapt_en, delete_event)
    else:
        document.wasGeneratedBy(adapt_en, delete_event, other_attributes={
            "ex:reason": f"{adaptation['reason']}",
        },)

    # Create association between activity and initiator agent:
    document.wasAssociatedWith(delete_event, initiator, other_attributes={
        "prov:role": "ex:Initiator",
    },)


def create_insert_adaptation(document, adaptation, initiator, a):
    """
    Function creates an insert adaptation entity and links it to to initiator, resource agents
    and event activity.

    :params document: ProvDocument to which the data is saved.
    :params adaptation: adaptation object
    :param initiator: adaptation initiator
    :param a: resource agent
    """

    # Create adaptation event activity:
    change_name = adaptation["change"]
    change_capitalized = change_name.title().replace(" ", "")
    insert_event = document.activity(f"ex:Adaptation{change_capitalized}", other_attributes={
        "prov:label": f"{adaptation['time']}",
    },)

    # Create an Adaptation entity:
    impact = adaptation["impact"]
    if impact == "":
        adapt_en = document.entity(f"ex:{adaptation['id']}", other_attributes={
            "ex:type": f"{adaptation['type']}",
            "ex:change": f"{adaptation['change']}",
        },)
    else:
        adapt_en = document.entity(f"ex:{adaptation['id']}", other_attributes={
            "ex:type": f"{adaptation['type']}",
            "ex:change": f"{adaptation['change']}",
            "ex:impact": f"{adaptation['impact']}",
        },)

    # Create attribution between initiator and entity:
    document.wasAttributedTo(adapt_en, initiator)
    # Create attribution between event resource and entity:
    document.wasAttributedTo(adapt_en, a)

    # Create generation between entity and activity
    reason = adaptation["reason"]
    if reason == "":
        document.wasGeneratedBy(adapt_en, insert_event)
    else:
        document.wasGeneratedBy(adapt_en, insert_event, other_attributes={
            "ex:reason": f"{adaptation['reason']}",
        },)

    # Create association between activity and initiator agent:
    document.wasAssociatedWith(insert_event, initiator, other_attributes={
        "prov:role": "ex:Initiator",
    },)
    

def create_event_terms(prov_document, event, instance_id):
    """
    Function creates terms based on PROV-O specification and adds them to a ProvDocument.

    :param prov_document: ProvDocument to which the data is added
    :param event: event data from results file
    :param instance_id: the ID of the instance being processed.
    """

    # create an instance bundle which groups all terms relevant to that instance:
    instance = prov_document.bundle(f"ex:{instance_id}")
    
    for e in event:
        ev = e["event"]
        adapt_initiator = e["adaptation_initiator"] 
        adaptation = e["adaptation"]

        resource = ev["resource"]

        # Create initiator agent only if initiator exists:
        if adapt_initiator is not None:
            initiator = prov_document.agent(f"ex:{adapt_initiator}")

        if resource == "":
            # Create adaptation of type delete
            create_delete_adaptation(instance, adaptation, initiator)
        else:
            # Set unique event resource as agent:
            a = prov_document.agent(f"ex:{resource}")

            # Check if event has insert adaptation:
            if adapt_initiator is not None:
                create_insert_adaptation(instance, adaptation, initiator, a)
            else:
                # Set event as activity:
                e = instance.activity(f"ex:{ev['id']}", other_attributes={
                    "ex:name": f"{ev['name']}",
                    "prov:label": f"{ev['time']}",
                },)
                # Create association between the action and agent:
                instance.wasAssociatedWith(e, a)



def generate_prov(json_dir):
    """
    Function represents results in given json_dir in PROV-O specification and saves the result
    in RDF and PNG formats in output/ directory. Additionally returns the result in TriG format
    which is then sent to the API view.

    :param jason_dir: directory where the result.json is saved.
    """

    # Walk through the directory and process one file at a time:
    for path, folders, files in os.walk(json_dir):

        for file in files:

            # If the file is not a JSON file, ignore it as it does not contain retrieved result:
            if file != "result.json":
                continue

            file_path = os.path.join(path, file)
            print("Generating PROV-O for result.json")

            # Load data from the result.json file
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Create a prov document:
            prov_document = pm.ProvDocument()
            prov_document.set_default_namespace("http://example.org/")
            # add namespace for custom attributes:
            prov_document.add_namespace("ex", "http://example.org/")

            # take each trace in the data and process it:
            for block in data:
                # save instance_id of the trace:
                instance_id = block.get("instance_id")
                create_event_terms(prov_document, block["events"], instance_id)

            output_dir = Path(json_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save the result to an RDF file in the prov_format directory
            prov_document.serialize(format="rdf", destination=str(output_dir /"prov_result.rdf"))

            # for debugging and checking the mapping, we can create a simple visualization:
            dot = prov_to_dot(prov_document)
            dot.write_png(str(output_dir /"prov_result_vis.png"))
            
            # Save the result so it can be returned to the API:
            result = Dataset()
            result.parse(str(output_dir /"prov_result.rdf"), format="trig")
    
    return result


