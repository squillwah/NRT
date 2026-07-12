
from tools.references.api import get_papers_filter, get_ris, get_ref
from tools.references.refdata import ristoref, component_set
import tools.help as h
import json

# Takes dict of {journal : count}, returns list of refdata dicts.
def get_reference_data(journals, *, v=False, saveall=True):
    pmcids = []
    for j in journals:
        if v: print(f"Fetching {journals[j]} latest articles from {j}...")
        pmcids.extend(get_papers_filter(journals[j], f"{j}[Journal]"))  # Grabs most recent. Can add sort functionality later depending on goals.
    if v: print(f"Total source pmcids: {len(pmcids)}")

    if v: print("Fetching RIS data...")
    raw_ris = get_ris(*pmcids)
    if v: print(*raw_ris)

    # Testing to verify some stuff about formats.
    if saveall:
        extra = h.mkdir(DIRECTORY / "extra")
        _json_filer(raw_ris, extra / "reference_ris.json")
        _json_filer(get_ref(*pmcids), extra / "reference_formatted.json")

    if v: print(f"Formalizing {len(raw_ris)} RIS entries...")
    ref_data = [ristoref(ris) for ris in raw_ris]
    if v: print(json.dumps(ref_data, indent=2))

    return ref_data

def _json_filer(data, filename):
    try:
        with open(filename, "x") as file: json.dump(data, file, indent=2)
        print(f"Saved to '{filename}'")
    except FileExistsError:
        if input(f"! '{filename}' already exists, overwrite? [y/n]: ").strip().lower() == "y":
            with open(filename, "w") as file: json.dump(data, file, indent=2)
            print(f"Saved to '{filename}'")
        else: print("Write cancelled")

if __name__ == "__main__":
    # Journals and their count in the set
    JOURNALS = {"BMJ": 25,
                "Nature": 25,
                "Lancet": 25,
                "NEJM": 25}
    DIRECTORY = h.mkdir("./data/reference_source")

    ref_data = get_reference_data(JOURNALS, v=True)
    print("Writing reference data to file...")
    _json_filer(ref_data, DIRECTORY / "refdata.json")

    print("Writing component set to file...")
    _json_filer(component_set(*ref_data), DIRECTORY / "compset.json")


