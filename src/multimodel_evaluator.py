

from tools.help import log
from tools.llms.schemas import ProtoSchemas
from tools.llms.orouterapi import openrouter, parse_response, trytryagain
from tools.references.refdata import ReferenceComponent
from tools.references.formats import FormatStyle
from shutil import copy2
import tools.help as h
import json
import random
import concurrent.futures
import threading

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
    response, t = trytryagain(openrouter, {"model": model, "ref": dsentry["format"]["elsevier"], "schema": schema})    # @TODO differentiate formats
    log(f"Time elapsed: {t} seconds", t="s")
    log(f"Parsing response and saving response dump to '{dsentry["id"]}_{model.split("/")[-1]}_{form}.json'", t="s")
    response = parse_response(response) # Parse is where we'd pull out tokens and other metrics. Return a result and a {metrics}.
    save_response_dump(response, f"{dsentry["id"]}_{model.split("/")[-1]}_{form}")

    return response["result"], t    # @TODO Could also return Token usage, but it can always be extracted from the dump postfact.

# Template for evaluated reference file structure
def results_template(dsentry, models):
    return {
        "id": dsentry["id"],
        "components": [c for c in ReferenceComponent]+["REFERENCE"],    # Just full list of components and the holistic REFERENCE. Mirrors compelte schema (untrimmed). # @TODO Should this be trimmed specific? Or a bool dict like in the dsentry? 
        "models": models,                                               # Metadata to help with csv and grading.
        "formats": {},
        "results": {m: {f: None for f in FormatStyle} for m in models}  # @TODO add time and token metrics (probably return as part of result in evaluate)
    }
def add_result(model, style, result, t, results): 
    results["results"][model][style] = {"metrics": {"time": t}, "response": result}      # Could include more metrics later (tokens etc), though most already exist in the dump (can be added on a second pass).
    if style not in results["formats"]: results["formats"][style] = [model] 
    elif model not in results["formats"][style]: results["formats"][style].append(model)

def safe_log(msg, t=None):
    with log_lock:
        log(msg, t=t)  # Replace with your actual logging function

def _evaluate_task(entry, model, style):
    return evaluate(entry, model, form=style)


TARGET_DIR = "./mme"
DATASET = "REFERENCES_NOSUG.json"
MODELS = (
    "deepseek/deepseek-v4-flash",                   # A couple of the most popular models (and nemotron) with text capabilities + response_format parameter support.
    "nvidia/nemotron-3-super-120b-a12b:free",       # https://openrouter.ai/models?supported_parameters=response_format&order=most-popular&input_modalities=text&output_modalities=text    
    "xiaomi/mimo-v2.5",
    "google/gemini-3-flash-preview"
)
# @TODO: Use papers with dates before knowledge cutoffs
# @TODO: Or specifiy current date in system prompt.
# @TODO: Could we use a LLM to analyze all the reasoning data? To detect trends, such as the issues with 'future' dates?
# @TODO: !!! Before the big test, make sure format compilers actually do what they say!
# @TODO: !! AND before the even bigger test, get down the variations in the dataset. The old test functions are not varied enough.

if __name__ == "__main__":
    open_files(TARGET_DIR)
    log(f"Testing references in '{DATASET}' against:")
    for m in MODELS: log(m, t="s") 
    
    log("Loading dataset, creating backup 'source.json' at root")
    save_dataset(DATASET)
    dataset = h.read_json(DATASET)

    log_lock = threading.Lock()

    # Trim to 5 for testing
    dataset = {ID: entry for ID, entry in list(dataset.items())[:5]}

    log(f"Beginning evaluation of {len(dataset)} references, with {len(MODELS)} models per reference")
    
    results_all = {ID: None for ID in dataset}

    max_workers = min(len(MODELS) * len(dataset), 15)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for ID, entry in dataset.items():
            log(f"Generating result template for {entry['id']}")
            results = results_template(entry, MODELS)

            # Queue all model evaluations for this entry
            future_to_model = {}
            for model in MODELS:
                style = random.choice(list(FormatStyle))

                with log_lock:
                    log(f"{ID} {model} {style}", t="h")

                future = executor.submit(_evaluate_task, entry, model, style)
                future_to_model[future] = (model, style)

            for future in concurrent.futures.as_completed(future_to_model):
                model, style = future_to_model[future]
                try:
                    result, t = future.result()

                    with log_lock:
                        log(f"{ID} {model} {style}", t="h")

                    if result:
                        add_result(model, style, result, t, results)
                    else:
                        with log_lock:
                            log("BADBAD! Result is null and was not added, something terrible must have happened.", t="e")
                except Exception as e:
                    with log_lock:
                        log(f"Failed evaluation for {model}: {e}", t="e")

            with log_lock:
                log(f"Saving full multimodel evaluation of ENTRY {ID} to '{ID}.json' and appending to 'all.json'")
            save_results(results, f"{ID}")
            results_all[ID] = results

        with log_lock:
            log(f"Saving all results to 'all.json'")
        save_results(results_all, "all")

    close_files()


# Some experiments to do regarding schema trimming
# See performance without schema trimming, but with disregarding chatbot answers
# See performance with schema trimming (so no answers in the first place)
# And of course the full load. How does the existence of the question effect their performance?

# old

# Groundwork for scaling.
# Testing two references against two models. 
# Save results into matrix.
# ! To @consider: should files be references and columns models, or vice versa? What is our z?
#      @consider: Should we enable reasoning?
#                 Testing result difference with deepseek, internet on and off.

