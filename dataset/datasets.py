
import reftools.ref_formatters as RB
import reftools.ref_mutators as RM
import random
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
    def __init__(self, *, component_set, fake_titles, fake_authors, fake_journals):
        # Mutation flags
        self._M_FLAGS = { "title_hallucinate": 0b0001,    # Some errors are not combinable.
                          "title_mismatch":    0b0010 }

        # Resources for hallucination and mismatch mutations
        self._COMPONENTS = component_set
        self._FAKE_TITLES = fake_titles
        self._FAKE_AUTHORS = fake_authors
        self._FAKE_JOURNALS = fake_journals

        # Alternatively, if we think a hallucination sample for every component is a good idea:
        # self._REAL_COMPONENTS
        # self._FAKE_COMPONENTS
        # The issue is, how fake can a date, DOI, or PMCID get? Fake enough to warrant that?

    def _flag(self, ds_entry, flag):
        ds_entry["errors"] = ds_entry["errors"] | self._M_FLAGS[flag]

    # AUTHORS

    # TITLES

    def title_typo(self, ds_entry):
        #RM.set_title
        pass

    def title_mismatch(self, ds_entry):
        RM.set_title(ds_entry["data"], random.choice(self._COMPONENTS["title"]))
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




