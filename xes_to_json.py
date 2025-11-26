import os
import json
from pm4py.objects.log.importer.xes import importer as xes_importer

def xes_to_json_converter(xes_location, json_dir_name):
    """
    This function converts XES files to JSON files.

    :param xes_location: the name of the directory of the XES files
    :param json_dir_name: the name of the directory where to store the JSON files
    """

    try:
        os.mkdir(json_dir_name)
        print("Directory " + json_dir_name + " created successfully.\n")
    except FileExistsError:
        print("Directory " + json_dir_name + " already exists.\n")
    except:
        print("An error occurred while creating the directory.\n")
        # If creating a directory results in a failure, return, it is not known where to store the JSON files
        return

    # os.walk goes through all subdirectories and returns a 3-tuple: the path, folders and files in the current directory
    for path, folders, files in os.walk(xes_location):
        for file in files:
            # In case a non-XES file is found, proceed with the next file
            if not file.endswith(".xes"):
                continue

            print ("Convert: " + file)
            # find the full XES path by joining the path and the file name
            xes_path = os.path.join(path, file)
            # Give the JSON file the same as the XES file
            json_file_name = file.replace(".xes", ".json")
            json_path = os.path.join(json_dir_name, json_file_name)
            # Recognizes the trace and event tags, the log becomes an object here
            log = xes_importer.apply(xes_path)
            json_data = []
            # In each trace, there are several events (one trace is one process instance)
            for trace in log:
                trace_attributes = {}
                # Store the trace attributes
                for key, value in trace.attributes.items():
                    trace_attributes[key] = str(value)

                case = {
                    "trace_attributes": trace_attributes,
                    "events": []
                }
                for event in trace:
                    event_data = {}
                    for k, v in event.items():
                        event_data[k] = str(v)
                    case["events"].append(event_data)
                json_data.append(case)


            # Write to JSON, ensure_ascii=False doesn't skip any unusual characters
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)

            print("Conversion to JSON completed.\n")


# Call the converter function. Attributes can be changed according to the desired locations of directories.
xes_to_json_converter("./xes_files", "./json_files")
