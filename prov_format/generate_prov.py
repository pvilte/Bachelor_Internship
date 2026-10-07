import prov.model as pm
from prov.dot import prov_to_dot
import json
import os

def create_delete_adaptation(document, adaptation, initiator):

    # Create adaptation event activity:
    change_name = adaptation["change"]
    change_capitalized = change_name.title().replace(" ", "")
    delete_event = document.activity(f"ex:Adaptation{change_capitalized}", other_attributes={
        "ex:adaptation_timestamp": f"{adaptation['time']}",
    },)
    # Create an Adaptation entity:
    impact = adaptation["impact"]
    if impact == "":
        adapt_en = document.entity(f"ex:{adaptation['id']}", other_attributes={
            "ex:adaptation_type": f"{adaptation['type']}",
            "ex:adaptation_change": f"{adaptation['change']}",
        },)
    else:
        adapt_en = document.entity(f"ex:{adaptation['id']}", other_attributes={
            "ex:adaptation_type": f"{adaptation['type']}",
            "ex:adaptation_change": f"{adaptation['change']}",
            "ex:adaptation_impact": f"{adaptation['impact']}",
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

    # Create adaptation event activity:
    change_name = adaptation["change"]
    change_capitalized = change_name.title().replace(" ", "")
    insert_event = document.activity(f"ex:Adaptation{change_capitalized}", other_attributes={
        "ex:adaptation_timestamp": f"{adaptation['time']}",
    },)
    # Create an Adaptation entity:
    impact = adaptation["impact"]
    if impact == "":
        adapt_en = document.entity(f"ex:{adaptation['id']}", other_attributes={
            "ex:adaptation_type": f"{adaptation['type']}",
            "ex:adaptation_change": f"{adaptation['change']}",
        },)
    else:
        adapt_en = document.entity(f"ex:{adaptation['id']}", other_attributes={
            "ex:adaptation_type": f"{adaptation['type']}",
            "ex:adaptation_change": f"{adaptation['change']}",
            "ex:adaptation_impact": f"{adaptation['impact']}",
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
    

def create_event_terms(document, event):

    for e in event:
        ev = e["event"]
        adapt_initiator = e["adaptation_initiator"] 
        adaptation = e["adaptation"]

        resource = ev["resource"]

        # Create initiator agent only if initiator exists:
        if adapt_initiator is not None:
            initiator = document.agent(f"ex:{adapt_initiator}")

        if resource == "":
            # Create adaptation delete
            create_delete_adaptation(document, adaptation, initiator)
        else:
            # Set event resource as agent:
            a = document.agent(f"ex:{resource}")

            # Check if event has insert adaptation:
            if adapt_initiator is not None:
                create_insert_adaptation(document, adaptation, initiator, a)
            else:
                # Set event as activity:
                e = document.activity(f"ex:{ev['id']}", other_attributes={
                    "prov:label": f"{ev['name']}",
                    "ex:timestamp": f"{ev['time']}",
                },)
                # Create association between the action and agent:
                document.wasAssociatedWith(e, a)



def generate_prov(json_dir):

    # Walk through the directory and process one file at a time:
    for path, folders, files in os.walk(json_dir):

        for file in files:
            file_path = os.path.join(path, file)
            print("Generating PROV-O for result.json")

            # Load data from the result.json file
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Create a prov document:
            document = pm.ProvDocument()
            document.set_default_namespace("http://example.org/")
            # add namespace for custom attributes:
            document.add_namespace("ex", "http://example.org/")

            # take each trace in the data and process it:
            for block in data:
                create_event_terms(document, block["events"])

            # Save the result to an RDF file in the prov_format directory
            document.serialize(format="rdf", destination="prov_format/prov_result.rdf")

            # for debugging and checking the mapping, we can create a visualization:
            dot = prov_to_dot(document)
            dot.write_png("prov_format/prov_result_vis.png")


if __name__ == "__main__":
    generate_prov("output")
    print("Generated a PROV-O document\n")

