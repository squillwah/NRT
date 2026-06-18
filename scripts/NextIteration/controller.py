import json
import time
from prompt_writer import generate_prompt
from openRouter_accessor import openrouter_accessor, openrouter_all_call


def printToFile(results, id):
    with open("./container/" + id+ ".json", "w") as f:
        json.dump(results, f, indent=4)

parsed_refs = {}

name = input("Please enter the json file name with the .json extension: ")

print("Loading from File . . .")
with open(name, 'r') as file:
    parsed_refs = json.load(file)

header_prompt = generate_prompt()
for i, ref in enumerate(parsed_refs):
    results = []
    ama_responses = openrouter_all_call(header_prompt, ref["ama"]["format"])
    results.append({
        "Citation_Type": "ama",
        "responses": ama_responses
    })
    time.sleep(1)

    apa_responses = openrouter_all_call(header_prompt, ref["apa"]["format"])
    results.append({
        "Citation_Type": "apa",
        "responses": apa_responses
    })
    time.sleep(1)

    mla_responses = openrouter_all_call(header_prompt, ref["mla"]["format"])
    results.append({
        "Citation_Type": "mla",
        "responses": mla_responses
    })
    time.sleep(1)

    nlm_responses = openrouter_all_call(header_prompt, ref["nlm"]["format"])
    results.append({
        "Citation_Type": "nlm",
        "responses": nlm_responses
    })
    time.sleep(1)

    ris_responses = openrouter_all_call(header_prompt, ref["ris"])
    results.append({
        "Citation_Type": "ris",
        "responses": ris_responses
    })
    time.sleep(1)

    printToFile(results, ref["id"].replace(":", "_"))



print("done!")