import os
import json
from pm4py.objects.log.importer.xes import importer as xes_importer

def xes_to_json_converter(xes_location, json_dir_name):

    try:
        #Create a directory for the JSON files
        os.mkdir(json_dir_name)
        print("Directory " + json_dir_name + " created successfully.\n")
    except FileExistsError:
        #The directory already exists
        print("Directory " + json_dir_name + " already exists.\n")
    except:
        #There was another error while trying to create this directory
        print("An error occurred while creating the directory.\n")




    #os.walk goes through all files and subdirectories of the given directory
    #os.walk always returns a 3-tuple: the current root of the path, a list of subdirectories and a list of files
    #in this directory
    #Each looping gives a unique 3-tuple
    for path, folders, files in os.walk(xes_location):
        #Examine the list of the returned files in this directory
        for file in files:
            #In case a non-XES file is found, proceed with the next file
            if not file.endswith(".xes"):
                continue

            #Join the root with the current file of the XES location
            xes_path = os.path.join(path, file)
            #Give the JSON file the same as the file has in the XES version
            json_file_name = file.replace(".xes", ".json")
            #Join the JSON path with the JSON directory
            json_path = os.path.join(json_dir_name, json_file_name)
            #Recognizes the trace and event tags, the log becomes an object here
            #With the following line I make a list of traces
            log = xes_importer.apply(xes_path)
            #Prepare an empty list where to store the json data
            json_data = []
            #In each trace, there are several events (one trace is one process instance)
            for trace in log:
                case = {
                    "events": []
                }
                for event in trace:
                    #Create an empty Python dictionary for the event data
                    #Dictionaries in Python is a data structure that stores key-value pairs
                    event_data = {}
                    #event.items() gives key-value pairs for each property, it is a tuple
                    for k, v in event.items():
                        #Add the new key value pair
                        event_data[k] = str(v)
                    #Add the new properties to the case
                    case["events"].append(event_data)
                #Add the case to the JSON data
                json_data.append(case)

            #A standard way to write JSON files
            #ensure_ascii=False doesn't skip any unusual characters id there is a need to store them
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)



xes_to_json_converter("./xes_files", "./json_files")
