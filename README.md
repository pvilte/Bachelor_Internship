# How to run the project

First, you will need to convert all the data from XES to JSON.
To do that, go to [xes_to_json.py](xes_to_json.py). Run this file. You should now
have a folder 'json_files' with the converted files.

Next, to record the store the information of the folder in a graph 
database, make sure your graph database is running. Go to 
[record.py](record/record.py), run this file.

```
python -m record.record
```

Now the data is stored in the database.

To retrieve data from the database, go to directory [retrieval](retrieve), then
[retrieve.py](retrieve/retrieve.py). Run this file by this command:
```
python -m retrieval.retrieve
```

It allows to interactively choose what 
to retrieve from the database. The resulting JSON file with the query should be saved in a file
in the main directory of the project.