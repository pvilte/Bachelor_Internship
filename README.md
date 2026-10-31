# Short description of the Bachelor Internship project


[xes_to_json.py](xes_to_json.py) converts all the data from XES to JSON.

[record.py](record/record.py) records the contents of the JSON files in a graph 
database.

[retrieval](retrieve) retrieves data from the database. It allows to interactively choose what 
to retrieve from the database. The resulting JSON file with the query should be saved in a file
in the main directory of the project.

[generate_prov.py](prov_format/generate_prov.py) creates a PROV-O document from the result.json file
and visualises the provenance in PNG format. 

[cli.py](cli.py) parses command-line arguments and calls selected functions:

| Command     | Description               |
|-------------|---------------------------|
| record      | calls [record.py](record/record.py)   |
| retrieve    | calls selected function from [retrieve](retrieve) (see below the arguments for different retrieval functions) |
| prov        | calls [generate_prov.py](prov_format/generate_prov.py) |

Please see [requirements.txt](requirements.txt) for dependencies.


# Running using Docker
First, please open your Docker Desktop.

Then, type in your terminal the following command:

```
docker compose build
```

First, if there are no XES files are converted to JSON format, run the folowing command in the terminal:
```
docker compose run --rm server python -m xes_to_json
```

To record the JSON files to the graph database, run the following command in the terminal:

```
docker compose run --rm server python -m cli record
```

To retrieve information from the database, run `docker compose run --rm server python -m cli retrieve` 
followed by what we want to retrive:

| Command                                       | Description               |
|-----------------------------------------------|---------------------------|
| all                                           | Retrieve all contents from the database   |
| direct_neighbours_collect node1 node2         | Retrieve all direct neighbours collected on a label |
| count all                                     | Retreive the count of all nodes in database  |
| count direct_neighbours node1 node2           | Retrieve count of nodes direct neighbours |
| count node_label label                        | Retrieve count of nodes with given label |
| count nodes_property label property value     | Retrieve count of nodes with specified property values |
| count all_relationships                       | Retrieve count of all relationships in database |
| nodes_label_property label property value     | Retrieve all nodes based on label and property value |
| node_relationship node1 node2                 | Retrieve relationship between two nodes |
| node_properties label                         | Retrieve node properties based on label |
| all_labels                                    | Retrieve all labels in database |
| all_relationships                             | Retrieve all relationships in database |
| disconnected_nodes                            | Retrieve all disconnected nodes in database |
| most_incomming_rel label                      | Retrieve node of most incomming relationships based on label |
| events_with_adapt                             | Retrieve all events with adaptations in database |
| reason_impact key                             | Retrieve reason, impact, or both of event adaptation |
| trace_single_instance instance_id             | Retreieve trace based on instance_id |
| all_traces                                    | Retreieve all traces from database |
| impact_of_instance instance_id                | Retreieve overall impact of instance |
 
Additionally, the query used in the retrieval will be displayed in the command-line interface (CLI)
which then can be copied and pasted directly to the Neo4j browser which can be accessed through: `http://localhost:7474/browser/`.

To convert retrieved results ([output/result.json](output/result.json)) to PROV-O format, use `--prov` after using `retrieve` command. The output given in RDF and PNG formats can then be viewed in the [output](output/) directory. 

The command bellow retrieves all traces from database and generates a PROV-O document for that result.

```
docker compose run --rm server python -m cli retrieve --prov all_traces
```

### Note: 

`--prov` will only work and generate an answer for the following retrieval cases:

- events_with_adapt
- trace_single_instance instance_id 
- all_traces


# Running API

To run the API of the project, in the terminal, run the following:

```
docker compose run --rm -p 8000:8000 server python manage.py runserver 0.0.0.0:8000
```

### Record

To record JSON format event data, simply use the following request: `http://localhost:8000/api/traces/`. In the content field add the data in JSON format. Finally, click on POST and if the recording is successful, yous should be able to see `"Recording complete!"` and then visualise the data in the Neo4j browser.

To record overall impact of instances, use the following request: `http://localhost:8000/api/trace/impact/`. In the content field add the impact data in JSON format. Finally, click on PUT and if the recording is successful, you should be able to see `"Recording complete!"` and visualise the data in the Neo4j browser.

### Retrieve

To view retrieved results in browser, add one of the endpoints specified in table below to http://localhost:8000/api/

| Endpoint                                      | Description               |
|-----------------------------------------------|---------------------------|
| all-traces/                                   | Retrieve all traces   |
| events-with-adapt/                            | Retrieve all events with adaptations |
| reason-impact/key/                            | Retreive reason or impact of adaptations (instead of 'key' input either reason, impact or both depending what you would like to retrieve)  |
| trace-single-instance/instance/               | Retrieve trace of an instance whose ID is specified instead of 'instance' |
| impact-of-instance/instance/                  | Retrieve impact of instance where 'instance' specified the instance ID|

### Generating PROV-O

To generate PROV-O for all-traces/, events-with-adapt/, and impact-of-instance/instance/, simply add `?type=prov` to the endpoint. The RDF file content will appear in the browser. 

For example, to generate PROV-O for a single trace with instance ID "Instance-95382", we use the following HTTP request: `http://localhost:8000/api/trace-single-instance/Instance-95382/?type=prov`.
