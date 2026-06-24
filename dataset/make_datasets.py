
from copy import deepcopy
import reftools.ref_mutators as RM
import reftools.ref_formatters as RB
import random
import json

# Builds datasets from a source reference file.
# Uses ref_mutators to create bad references/datasets.
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

# Class of methods to mutate dataset entries using ref_mutator functions.
class DSEntryMutator:
    def __init__(self, *, component_f, title_f):
        # For use in some error types
        #  Component set
        self._COMPONENT_SET = None
        with open(component_f, "r") as f:
            self._COMPONENT_SET = json.load(f)
        #  Hallucinated titles
        self._FAKE_TITLES = None
        with open(title_f, "r") as f:
            self._FAKE_TITLES = [line.strip() for line in f if line.strip()]
        # Error code flags
        self._M_FLAGS = { "title_hallucinate": 0b0001,    # Some errors are not combinable.
                          "title_mismatch":    0b0010 }

    def _flag(self, ds_entry, flag):
        ds_entry["errors"] = ds_entry["errors"] | self._M_FLAGS[flag]

    def title_hallucinate(self, ds_entry):
        RM.set_title(ds_entry["data"], random.choice(self._FAKE_TITLES))
        self._flag(ds_entry, "title_hallucinate")
        return ds_entry # Note: returns reference for convenience. It is not a copy.

    def title_mismatch(self, ds_entry):
        COMPONENTS = {"title": ["one", "two", "ASS!", "the wrong title"]}  # Placeholder until component_set is fixed
        RM.set_title(ds_entry["data"], random.choice(COMPONENTS["title"])) # self._COMPONENT_SET["title"]
        self._flag(ds_entry, "title_mismatch")
        return ds_entry

# Creating datasets from reference_data.json, mutating references with EntryMutator.
if __name__ == "__main__":
    ref_data = None
    with open("./data/reference_data.json", "r") as f:
        ref_data = json.load(f)


    # Create sets of ds_entries for source references, hallucinated title references, and mismatched title references. @todo: more
    source_ds = create_dataset(ref_data, v=True)
    title_hallucinate_ds = create_dataset(ref_data[0:25], v=True)
    title_mismatch_ds = create_dataset(ref_data[25:50], v=True)

    # Applying title mutations.
    M = DSEntryMutator(title_f="./data/fake_titles.txt", component_f="./data/component_set.json")
    for entry in title_hallucinate_ds:
        M.title_hallucinate(entry)
    for entry in title_mismatch_ds:
        M.title_mismatch(entry)

    # Combining datasets and baking reference formats.
    complete_ds = source_ds + title_hallucinate_ds + title_mismatch_ds
    for entry in complete_ds:
        entry["format"] = RB.bake_formats(entry["data"])

    print(json.dumps(complete_ds, indent=2))
