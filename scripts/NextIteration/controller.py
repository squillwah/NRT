import json
import time
from prompt_writer import generate_prompt
from openRouter_accessor import openrouter_all_call
from tests.CSV_Testing import write_xlsx


# This method writes the output generated per paper's citation and dumps all the responses from the LLMs into one JSON File
def printToFile(results, id):
    with open("./container/" + id+ ".json", "w") as f:
        json.dump(results, f, indent=4)

def main():

    parsed_refs = {} # empty dictionary used to load all the references from the json file
    name = input("Please enter the json file name with the .json extension: ") # user can enter the json file name that holds all the references

    # this loads the json file entered above into the empty dictionary
    print("Loading from File . . .")
    with open(name, 'r') as file:
        parsed_refs = json.load(file)

    header_prompt = generate_prompt() # this calls the prompt_writer.py function to set up the header portion of the API call.

    responses_for_CSV = []
    list_of_ids = []

    # this loops through every ama citation style in the parsed references and makes the call to openrouter_all_call, for which will go through every LLM and finally return a dictionary which will get dumped to the json file.
    for i, ref in enumerate(parsed_refs):
        ama_responses = openrouter_all_call(header_prompt, ref["format"]["ama"])
        time.sleep(1)

        responses_for_CSV.append(ama_responses)
        list_of_ids.append(ref["id"].replace(":", "_"))

        printToFile(ama_responses, ref["id"].replace(":", "_"))

    write_xlsx(responses_for_CSV, list_of_ids)
    print("done!")


#main method
if __name__ == "__main__":
    main()