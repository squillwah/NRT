import json
import time
from prompt_writer import generate_prompt
from openRouter_accessor import openrouter_accessor

def printToFile(results, id):
    with open("./container/" + id+ ".json", "w") as f:
        json.dump(results, f, indent=4)

parsed_refs = {}

name = input("Please enter the json file name with the .json extension: ")

with open(name, 'r') as file:
    parsed_refs = json.load(file)

header_prompt = generate_prompt()
print("Started API Requests")
for i, ref in enumerate(parsed_refs):
    results = []
    jsonObject = openrouter_accessor(header_prompt, ref["ama"]["format"])
    results.append(jsonObject)
    time.sleep(1)

    jsonObject = openrouter_accessor(header_prompt, ref["apa"]["format"])
    results.append(jsonObject)
    time.sleep(1)
    
    jsonObject = openrouter_accessor(header_prompt, ref["mla"]["format"])
    results.append(jsonObject)
    time.sleep(1)
    
    jsonObject = openrouter_accessor(header_prompt, ref["nlm"]["format"])
    results.append(jsonObject)
    time.sleep(1)
    
    jsonObject = openrouter_accessor(header_prompt, ref["ris"])
    results.append(jsonObject)
    time.sleep(1)
    
    printToFile(results, ref["id"].replace(":", "_"))


print("done!")