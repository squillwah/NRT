
from tools.help import log 
from tools.llms.schemas import ProtoSchemas
from tools.llms.orouterapi import openrouter, parse_response, trytryagain
from tools.references.refdata import ReferenceComponent
from tools.references.formats import FormatStyle
from shutil import copy2
import tools.help as h
import json
import random
#import time
#import os

# @todo add keys array to JSON output.

# Groundwork for scaling.
# Testing two references against two models. 
# Save results into matrix.
# ! To @consider: should files be references and columns models, or vice versa? What is our z?
#      @consider: Should we enable reasoning?
#                 Testing result difference with deepseek, internet on and off.


# Set up output files
save_dataset = None
save_results = None
save_response_dump = None
def open_files(root):
    d_root = h.mkdir(root, timestamp=True)
    d_results = h.mkdir(d_root / "results")
    d_response_dumps = h.mkdir(d_root / "dumps")
    h.open_log(d_root / "log")
    log("Directory:", str(d_root), t="h")

    global save_dataset, save_results, save_response_dump
    save_dataset = lambda filename: copy2(filename, d_root / "source.json")
    save_results = lambda result, name: h.write_json(result, f"{d_results}/{name}.json")
    save_response_dump = lambda dump, name: h.write_json(dump, f"{d_response_dumps}/{name}.json")
# Clean up
def close_files(): 
    global save_dataset, save_results, save_response_dump
    save_dataset, save_results, save_response_dump = None, None, None
    h.close_log()

# Query openrouter for response, save dump to file and return model output
def evaluate(dsentry, model, form=None):
    schema = ProtoSchemas.make_schema(ProtoSchemas.make_schema_properties())        # Later on this can be tailored. A "prompt trimming" experiment (make it easier on the AI).
    log("Requesting Openrouter", t="s")
    response = trytryagain(openrouter, {"model": model, "ref": dsentry["format"]["elsevier"], "schema": schema})    # @TODO differentiate formats
    log("Parsing response", t="s")
    response = parse_response(response)     # @TODO record time ....
    log(f"Saving response dump to '{dsentry["id"]}_{model.split("/")[-1]}_{form}.json'", t="s")
    save_response_dump(response, f"{dsentry["id"]}_{model.split("/")[-1]}_{form}")
    return response["result"]

# Template for evaluated reference file structure
def results_template(dsentry, models):
    return {
        "id": dsentry["id"],
        "components": [c for c in ReferenceComponent]+["REFERENCE"],    # Just full list of components and the holistic REFERENCE. Mirrors compelte schema (untrimmed). # @TODO Should this be trimmed specific? Or a bool dict like in the dsentry? 
        "models": models,                                               # Metadata to help with csv and grading.
        "formats": {},
        "results": {m: {f: None for f in FormatStyle} for m in models}  # @TODO add time and token metrics (probably return as part of result in evaluate)
    }
def add_result(model, style, result, results): 
    results["results"][model][style] = result
    if style not in results["formats"]: results["formats"][style] = [model] 
    elif model not in results["formats"][style]: results["formats"][style].append(model)

MODELS = ("deepseek/deepseek-v4-flash", "nvidia/nemotron-3-super-120b-a12b:free")
DATASET = "THEREFERENCES_IDKEYS.json"
TARGET_DIR = "./mme"

if __name__ == "__main__":
    open_files(TARGET_DIR)
    log(f"Testing references in '{DATASET}' against:")
    for m in MODELS: log(m, t="s") 
    
    log("Loading dataset, creating backup 'source.json' at root")
    save_dataset(DATASET)
    dataset = h.read_json(DATASET)

    # Trim to 2 for testing
    dataset = {ID: entry for ID, entry in list(dataset.items())[:2]}

    log(f"Beginning evaluation of {len(dataset)} references, with {len(MODELS)} models per reference")
    
    results_all = {ID: None for ID in dataset}
    for ID, entry in dataset.items():
        log(f"Generating result template for {entry["id"]}")
        results = results_template(entry, MODELS)
        
        log(f"Iterating models...")
        for model in MODELS:
            style = random.choice(list(FormatStyle))        # @TODO Pick formats intelligently? Is random a good metric, or should we weight by 'popularity' (whatever that may be).
            
            log(f"{ID} {model} {style}", t="h")
            result = evaluate(entry, model, form=style)
            
            log(f"Adding result: {model} ({style})", t="s")
            if result: add_result(model, style, result, results)
            else: log("BADBAD! Result is null and was not added, something terrible must have happened.", t="e")
        
        log(f"Saving full multimodel evaluation of ENTRY {ID} to '{ID}.json' and appending to 'all.json'")
        save_results(results, f"{ID}")
        results_all[ID] = results

    log(f"Saving all results to 'all.json'")
    save_results(results_all, "all")

    
    close_files()


# Some experiments to do regarding schema trimming
# See performance without schema trimming, but with disregarding chatbot answers
# See performance with schema trimming (so no answers in the first place)
# And of course the full load. How does the existence of the question effect their performance?

"""

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

"""
