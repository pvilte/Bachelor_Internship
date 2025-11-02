# Short description of the Bachelor Internship project


[xes_to_json.py](xes_to_json.py) converts all the data from XES to JSON.

[record.py](record/record.py) records the contents of the JSON files in a graph 
database.

[retrieval](retrieve) retrieves data from the database. It allows to interactively choose what 
to retrieve from the database. The resulting JSON file with the query should be saved in a file
in the main directory of the project.

Please see [requirements.txt](requirements.txt) for dependencies.


# Running using Docker
First, please open your Docker Desktop.

Then, type in your terminal the following command:

```
docker compose build
```

Depending on which files you would like to run, choose between these 3 commands:
```
docker compose run --rm server python -m xes_to_json
```

```
docker compose run --rm server python -m record.record
```

```
docker compose run --rm server python -m retrieve.retrieve
```

Please see http://localhost:7474/browser/ for querying the database.