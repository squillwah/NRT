import json
import time
from prompt_writer import generate_prompt
from openRouter_accessor import openrouter_all_call


def printToFile(results, id):
    with open("./container/" + id+ ".json", "w") as f:
        json.dump(results, f, indent=4)

parsed_refs = {}

name = input("Please enter the json file name with the .json extension: ")

print("Loading from File . . .")
with open(name, 'r') as file:
    parsed_refs = json.load(file)

ids = []
header_prompt = generate_prompt()
for i, ref in enumerate(parsed_refs):
    ama_responses = openrouter_all_call(header_prompt, ref["ama"]["format"])
    time.sleep(1)

    ids.append(ref["id"].replace(":", "_"))
    printToFile(ama_responses, ref["id"].replace(":", "_"))
    print(ids)



print("done!")