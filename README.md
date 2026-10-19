# Short description of the Bachelor Internship project


[xes_to_json.py](xes_to_json.py) converts all the data from XES to JSON.

[record.py](record/record.py) records the contents of the JSON files in a graph 
database.

[retrieval](retrieve) retrieves data from the database. It allows to interactively choose what 
to retrieve from the database. The resulting JSON file with the query should be saved in a file
in the main directory of the project.

[generate_prov.py](prov_format/generate_prov.py) creates a PROV-O document from the result.json file
and visualises the provenance in PNG format. 

[program.py](program.py) parses command-line arguments and calls selected functions:

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
docker compose run --rm server python -m program record
```

To retrieve information from the database, run `docker compose run --rm server python -m program retrieve` 
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

To convert retrieved results ([output/result.json](output/result.json)) to PROV-O format, run the
command below. The output given in RDF and PNG formats can then be viewed in the [output](output/) directory.

```
docker compose run --rm server python -m program prov
```
