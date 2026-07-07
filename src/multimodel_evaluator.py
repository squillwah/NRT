
from tools.llms.schemas import ProtoSchemas
from tools.llms.orouterapi import openrouter, parse_response, trytryagain
from tools.help import log, write_json
from pathlib import Path
import json
import time
import os

# @todo add keys array to JSON output.

# Groundwork for scaling.
# Testing two references against two models. 
# Save results into matrix.
# ! To @consider: should files be references and columns models, or vice versa? What is our z?
#      @consider: Should we enable reasoning?
#                 Testing result difference with deepseek, internet on and off.


DATASET_FILE = "REFERENCE_DATASET2.json"
OUTPUT_DIR = f"mme{int(time.time())}"
MODELS = (
        #    "openai/gpt-oss-20b:free",
        #    "google/gemma-4-31b-it:free"
    "deepseek/deepseek-v4-flash",
    "nvidia/nemotron-3-super-120b-a12b:free"
)


# Load JSON ds file
def load_ds(filename):
    refds = None
    with open(f"{filename}", "r") as f: refds = json.load(f)
    return refds

# Flatten and randomize ds entries  @todo: Restructure ds into a top level ds metadata dict (with stuff like categorie count, ref count), and a list of {category: name, entries: ents} for each cat.
def randomize_ds(ds):
    # PLACEHOLDER
    entries = [ds["source"][3], ds["human_review"][3]]    # Structure of refdata (as in split into "source", "mderror", etc.) categories may change. We'll do some randomized order, maybe? idk.
    return entries

# Test a model against reference in specified format.
def evaluate_dsentry(model, dsentry, form):
    ref = dsentry["format"][form]                                                       # [form]["reference"]
    schema = ProtoSchemas.make_schema(ProtoSchemas.make_schema_properties(1))           # make_schema_properties(dsentry["format"][form]["compcode"]  Eventually
    log("Requesting openrouter...")
    response = parse_response(trytryagain(openrouter, {"model": model, "ref": ref, "schema": schema}))
    # Save full dump of response to a file, in case something terrible happens. 
    log(f"Saving response dump of ID{dsentry["id"]}_F{form} to file")
    write_json(response, f"./{OUTPUT_DIR}/id_{dsentry["id"]}_fmt_{form}_responsedump.json")
    return response["content"]  # Return the (hopefully) structured response from LLM.          @todo if we switch to tool use in the future, this gotta be redone someway.

# Test a model with a dataset entry (reference). All formats or specified list.
def evaluate_dsentry_multiformat(model, dsentry, formats=None):
    if not formats: formats = dsentry["format"].keys()
    elif isinstance(formats, str): formats = (formats,)
    return {form: evaluate_dsentry(model, dsentry, form) for form in formats}   # {format: evaluation}

if __name__ == "__main__":
    log("-"*50, t="")

    log(f"Loading {DATASET_FILE}")
    dataset = load_ds(DATASET_FILE)

    log(f"Creating output directory {OUTPUT_DIR}")
    Path(f"./{OUTPUT_DIR}").mkdir()

    log("Extracting references")
    dsentries = randomize_ds(dataset)
    for e in dsentries: log(f"RefID: {e["id"]}", t="s")

    # With formats, should we be mixing them in the same data?
    # For the general test, yeah who cares. Best not to get stuck on it.

    # Format (subject to change). Is it annoying to have them under formats like that?
    # {
    #   "ref": <copy of the dsentry>
    #   "results": {
    #       <model1>: {
    #           <format>: <result>
    #           <format>: <result>
    #       }
    #       <model2>: {
    #           <format>: <result>
    #       }
    #   }
    # }

    log("Beginning...")
    for dsentry in dsentries:   # @consider: Files as refs or files as models?
        refresults = { "ref": dsentry, "results": {m: {} for m in MODELS}}                          # Hopefully the dsentries aren't being modified. Why would they be?
        for model in MODELS:
            form = "elsevier"        # Add variation later @todo
            log(f"Evaluating {form} formatted RefID {dsentry["id"]} with {model}")
            result = evaluate_dsentry(model, dsentry, form)
            refresults["results"][model][form] = result
            if not result: log("Uh oh, that one was null.", t="e")
            else: result
            log(f"Saving results of RefID {dsentry["id"]} to 'ID{dsentry["id"]}.json'")
            write_json(refresults, f"./{OUTPUT_DIR}/id_{dsentry["id"]}.json")
        log(f"End of RefID {dsentry["id"]}")


