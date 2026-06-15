import json

from prompt_writer import generate_prompt
from openRouter_accessor import openrouter_accessor

def printToFile(list, i):
    with open(list[i]["id"]+".json", "w") as f:
        json.dump(results, f, indent=4)

parsed_refs = {}

name = input("Please enter the json file name with the .json extension: ")

with open(name, 'r') as file:
    parsed_refs = json.load(file)

header_prompt = generate_prompt()

print("done")
for i in parsed_refs:
    results = []
    jsonObject = openrouter_accessor(header_prompt, parsed_refs[i]["ama"]["format"])
    results.append(jsonObject)

    jsonObject = openrouter_accessor(header_prompt, parsed_refs[i]["apa"]["format"])
    results.append(jsonObject)

    jsonObject = openrouter_accessor(header_prompt, parsed_refs[i]["mla"]["format"])
    results.append(jsonObject)

    jsonObject = openrouter_accessor(header_prompt, parsed_refs[i]["nlm"]["format"])
    results.append(jsonObject)

    jsonObject = openrouter_accessor(header_prompt, parsed_refs[i]["ris"]["format"])
    results.append(jsonObject)

    printToFile(results, i)

print("done!")