
import reftools.ref_formatters as RB
import reftools.ref_mutators as RM
from copy import deepcopy

# Create a set entry from reference data
def ds_entry(rd):
    return { "id": rd["pmcid"],        # Should we use PMID, PMCID, or some internal thing (just in index?).
             "errors": 0b00000000,
             "data": deepcopy(rd),
             "format": {} }

# Create a set of set entries from a list of reference data
def create_dataset(ref_data_list, *, v=False):
    dataset = [ds_entry(ref) for ref in ref_data_list]
    return dataset

# Bake formatted references from refdata for every entry in a dataset
def bake_formats(dataset):
    for entry in dataset:
        entry["format"] = RB.bake_formats(entry["data"])

# Class of methods to mutate dataset entries using ref_mutator functions.
class EntryMutator:
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

    # AUTHORS

    # TITLES

    def title_typo(self, ds_entry):
        RM.set_title

    def title_mismatch(self, ds_entry):
        COMPONENTS = {"title": ["one", "two", "ASS!", "the wrong title"]}  # Placeholder until component_set is fixed
        RM.set_title(ds_entry["data"], random.choice(COMPONENTS["title"])) # self._COMPONENT_SET["title"]
        self._flag(ds_entry, "title_mismatch")
        return ds_entry

    def title_hallucinate(self, ds_entry):
        RM.set_title(ds_entry["data"], random.choice(self._FAKE_TITLES))
        self._flag(ds_entry, "title_hallucinate")
        return ds_entry # Note: returns reference for convenience. It is not a copy.


    # JOURNAL NAMES

    # JOURNAL PUBLICATION DATES

    # JOURNAL VOLUME / ISSUE

    # JOURNAL PAGE NUMBERS

    # DOI

    # PMIDS / PMCIDS



