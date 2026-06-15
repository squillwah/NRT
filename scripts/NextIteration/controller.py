import json

from NRT.scripts.NextIteration.prompt_writer import generate_prompt


parsed_refs = {}

name = input("Please enter the json file name with the .json extension: ")

with open(name, 'r') as file:
    parsed_refs = json.load(file)

print(parsed_refs[2]["apa"]["orig"])

header_prompt = generate_prompt()

print("done")
'''
response = Gemini.send_prompt("gemma-4-26b-a4b-it", header_prompt + )
print("\nThe response is: \n\n", Gemini.parse_response(response))'''