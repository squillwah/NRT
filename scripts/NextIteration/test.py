import json
print("Loading from File . . .")
with open("finkle.json", 'r') as file:
    parsed_refs = json.load(file)

    print(parsed_refs["format"]["ama"])