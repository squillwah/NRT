
from source_refs import get_papers_filter, get_ris#extract_reference_formats
from parse_refs import parse_ris, component_set
from copy import deepcopy
import ref_mutators as RM
import ref_builders as RB
import json

# Again, no error handling in any of this. Will break if it breaks.


# Create a set entry from reference data
def ds_entry(rd):
    return { "id": rd["pmcid"],        # Should we use PMID, PMCID, or some internal thing (just in index?).
             "errors": 0b00000000,
             "data": deepcopy(rd),
             "format": {} }

# Create a set of set entries from a list of reference data
def create_dataset(ref_data_list, *, v=False):
    if v: print(f"Creating dataset from {len(ref_data_list)} references...")
    dataset = [ds_entry(ref) for ref in ref_data_list]
    return dataset

# Takes dict of {journal : count}, returns list of refdata dicts.
def get_reference_data(journals, *, v=False):
    pmcids = []
    for j in journals:
        if v: print(f"Fetching {journals[j]} articles from {j}...")
        pmcids.extend(get_papers_filter(journals[j], f"{j}[Journal]"))  # Grabs most recent. Can add sort functionality later depending on goals.
    if v: print(f"Total source pmcids: {len(pmcids)}")

    if v: print("Fetching RIS data...")
    raw_ris = get_ris(*pmcids)
    if v: print(*raw_ris)

    if v: print(f"Formalizing {len(raw_ris)} RIS entries...")
    ref_data = [parse_ris(ris) for ris in raw_ris]
    if v: print(json.dumps(ref_data, indent=2))

    return ref_data

# Returns dict of {reference style : reference string}
def bake_formats(ref_data, *, v=False):
    if v: print(f"Baking {len(RB.FORMATS)} reference formats for {ref_data["pmcid"]}...")
    formats = {f: RB.build_ref(ref_data, f) for f in RB.FORMATS}
    return formats

if __name__ == "__main__":
    # Journals and their count in the set
    JOURNALS = {"BMJ": 25,
                "Nature": 25,
                "Lancet": 25,
                "NEJM": 25}

    ref_data = get_reference_data(JOURNALS, v=True)

    source_ds = create_dataset(ref_data, v=True)
    mauth_ds = create_dataset(ref_data, v=True)
    for entry in mauth_ds:
        entry["errors"] = entry["errors"] | 2 # RM.M_AUTHSWAP code placeholder
        entry["data"]["authors"] = ["bob", "billy", "joe"]

    complete_ds = source_ds + mauth_ds
    for entry in complete_ds:
        entry["format"] = bake_formats(entry["data"])

    print(json.dumps(complete_ds, indent=2))


