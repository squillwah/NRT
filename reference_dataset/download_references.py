
from api_tools import get_papers_filter, get_ris
from ris_parser import parse_ris
import json

# Takes dict of {journal : count}, returns list of refdata dicts.
def get_reference_data(journals, *, v=False):
    pmcids = []
    for j in journals:
        if v: print(f"Fetching {journals[j]} latest articles from {j}...")
        pmcids.extend(get_papers_filter(journals[j], f"{j}[Journal]"))  # Grabs most recent. Can add sort functionality later depending on goals.
    if v: print(f"Total source pmcids: {len(pmcids)}")

    if v: print("Fetching RIS data...")
    raw_ris = get_ris(*pmcids)
    if v: print(*raw_ris)

    if v: print(f"Formalizing {len(raw_ris)} RIS entries...")
    ref_data = [parse_ris(ris) for ris in raw_ris]
    if v: print(json.dumps(ref_data, indent=2))

    return ref_data

def _json_filer(data, filename):
    try:
        with open(filename, "x") as file: json.dump(ref_data, file, indent=2)
        print(f"Saved to '{filename}'")
    except FileExistsError:
        if input(f"! '{filename}' already exists, overwrite? [y/n]: ").strip().lower() == "y":
            with open(filename, "w") as file: json.dump(ref_data, file, indent=2)
            print(f"Saved to '{filename}'")
        else: print("Write cancelled")

if __name__ == "__main__":
    # Journals and their count in the set
    JOURNALS = {"BMJ": 25,
                "Nature": 25,
                "Lancet": 25,
                "NEJM": 25}
    DIRECTORY = "./data"

    ref_data = get_reference_data(JOURNALS, v=True)
    print("Writing reference data to file...")
    _json_filer(ref_data, f"{DIRECTORY}/reference_data.json")

    if input("Save component set too? [y/n]: ").strip().lower() == "y":
        #_json_filer(component_set(ref_data), f"{DIRECTORY}/component_set.json") @todo fix component_set
        pass





