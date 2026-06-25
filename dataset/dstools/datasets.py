
from copy import deepcopy
from reftools.typos import Typofier as T
import reftools.ref_formatters as RB
import random

# Create a set entry from reference data
def ds_entry(rd, *, ID=None):
    return { "id": ID,                  # Internal ID + original PMCID
             "src_id": rd["pmcid"],
             "mutcode": 0b00000000,
             "mutlabels": [],
             "data": deepcopy(rd),
             "format": {} }

# Create a set of set entries from a list of reference data
def make_dataset(ref_data_list, *, v=False):
    dataset = [ds_entry(ref, ID=i) for i, ref in enumerate(ref_data_list)]
    return dataset

# Bake formatted references from refdata for every entry in a dataset.
# Also adds a human readable list of mutation labels.
def bake_dataset(dataset):
    for entry in dataset:
        entry["format"] = RB.bake_formats(entry["data"])
        entry["mutlabels"] = EntryMutator.explain_mutcode(entry["mutcode"])

# Class of methods to mutate dataset entries using ref_mutator functions.
class EntryMutator:
    # Mutation flags:  
    _MLABELS = ("author_typo",    "author_mismatch",  "author_hallucinate",   "author_shuffle",   # Note: not all mutations are combinable.
                "title_typo",     "title_mismatch",   "title_hallucinate",                        # Also, be wary in the setting of these flags. A wrongly set flag will not reveal itself.
                "jname_typo",     "jname_mismatch",   "jname_hallucinate",
                "jvol_randomize", "jiss_randomize")
    _MFLAGS = {flag: 2**i for i, flag in enumerate(_MLABELS)} # Assign a unique bit for every flag.

    def __init__(self, *, component_set, h_titles, h_authors, h_journals):
        # Resources for hallucination and mismatch mutations
        self._COMPONENTS = component_set            # Alternatively, if we think a hallucination sample for every component is a good idea:
        self._FAKE_TITLES = h_titles                # self._REAL_COMPONENTS
        self._FAKE_AUTHORS = h_authors              # self._FAKE_COMPONENTS
        self._FAKE_JOURNALS = h_journals            # The issue is, how fake can a date, DOI, or PMCID get? Fake enough to warrant that?

### little helpers

    # Return list of mutation labels from mutcode.
    @classmethod
    def explain_mutcode(cls, code):
        return [label for label in cls._MFLAGS if (code & cls._MFLAGS[label])]
    # Set mutation flag in ds_entry.
    @classmethod
    def _flag(cls, ds_entry, flag):
        ds_entry["mutcode"] = ds_entry["mutcode"] | cls._MFLAGS[flag]       # @todo !!!! Some mutations undo other ones (like running a mismatch or hallucination after a type).
    # Return deepcopy of random item from collection.
    @staticmethod
    def _randcopy(collection):
        return deepcopy(random.choice(collection))

### AUTHORS

    # For no good reason, author typo logic is different from T.typofy().
    def author_typo(self, ds_entry):
        # ! Regarding typos, the question is which kind and how many. What range of randomness do we want and why?      # Perhaps (if we care), there is a paper. 
        # As a completely arbitrary heuristic, let it be that:                                                          # This one? https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7546536
        #  - There is a 1/4 chance for a typo to appear in an author's name. 
        #  - Some considerations are made for appearing in the final formats:
        #    - Typos are added to both the last and first names simultaneously.
        #    - The first three authors are guaranteed to have at least one typo.
        #  - Compounding typo's follow the natural halving of the probability (2: 1/8, 3: 1/16, so on)
        #  - Fatfingers are twice as likely as swaps (moved into typofier.fatswap)
        TYPO_CHANCE = 1/3
        authors = ds_entry["data"]["authors"]
        for author_i, name in enumerate(authors):
            first_three_guarantee = author_i > 2
            while random.random() <= TYPO_CHANCE or not first_three_guarantee:
                for part in name:
                    if name[part]: # Skip over empty names.
                        print(" ? ", name, part)
                        letter_i = random.choice([i for i, letter in enumerate(name[part])]) # if letter.isalpha()]) # Don't bother with spaces.    !!! Alpha check was causing oobs and empty set errors when following a fatfinger that added nonalphas or perhaps just some other weird RIS bugs.
                        #name[part] = RM.typo_fatfinger(name[part], letter_i) if random.random() <= FATSWAP_RATIO else RM.typo_swapletter(name[part], letter_i)
                        name[part] = T.fatswap(name[part], letter_i)
                first_three_guarantee = True
        self._flag(ds_entry, "author_typo")
        return ds_entry # Note: Reference returns are for convenience. They are not copies.

    def author_shuffle(self, ds_entry):
        random.shuffle(ds_entry["data"]["authors"])
        self._flag(ds_entry, "author_shuffle")
        return ds_entry

    def author_mismatch(self, ds_entry):
        ds_entry["data"]["authors"] = self._randcopy(self._COMPONENTS["authors"])
        self._flag(ds_entry, "author_mismatch")
        return ds_entry

    def author_hallucinate(self, ds_entry):
        #ds_entry["data"]["authors"] = self._randcopy(self._FAKE_AUTHORS)    # It needs to be a list of fake authors.

        ds_entry["data"]["authors"] = deepcopy(random.sample(self._FAKE_AUTHORS, len(ds_entry["data"]["authors"])))    # Making it the same length. Could be different. Who cares?
        self._flag(ds_entry, "author_hallucinate")
        return ds_entry

### TITLES

    def title_typo(self, ds_entry):
        ds_entry["data"]["title"] = T.typofy(ds_entry["data"]["title"])
        self._flag(ds_entry, "title_typo")
        return ds_entry
    def title_mismatch(self, ds_entry):
        #RM.set_title(ds_entry["data"], random.choice(self._COMPONENTS["title"]))   # Screw the ref_mutator shit
        ds_entry["data"]["title"] = self._randcopy(self._COMPONENTS["title"])
        self._flag(ds_entry, "title_mismatch")
        return ds_entry
    def title_hallucinate(self, ds_entry):
        #RM.set_title(ds_entry["data"], random.choice(self._FAKE_TITLES))
        ds_entry["data"]["title"] = self._randcopy(self._FAKE_TITLES)
        self._flag(ds_entry, "title_hallucinate")
        return ds_entry

### JOURNAL NAMES                                               # @todo: Think about: Should we be bothering with replacing each journal element like this, or should we just mismatch the whole thing together (name, date, volume, iss, pages)?

    def jname_typo(self, ds_entry):
        ds_entry["data"]["journal"]["name"]["short"] = T.typofy(ds_entry["data"]["journal"]["name"]["short"])
        ds_entry["data"]["journal"]["name"]["full"] = T.typofy(ds_entry["data"]["journal"]["name"]["full"])
        self._flag(ds_entry, "jname_typo")
        return ds_entry
    def jname_mismatch(self, ds_entry):
        ds_entry["data"]["journal"]["name"] = self._randcopy([jname for jname in self._COMPONENTS["jname_set"] if jname != ds_entry["data"]["journal"]["name"]])
        self._flag(ds_entry, "jname_mismatch")
        return ds_entry
    def jname_hallucinate(self, ds_entry):
        ds_entry["data"]["journal"]["name"] = self._randcopy(self._FAKE_JOURNALS)    # @todo: !! Make sure the fake_journal source contains both full and short names, and that the file is parsed into the proper dict format!
        self._flag(ds_entry, "jname_hallucinate")
        return ds_entry

### JOURNAL VOLUME / ISSUE

    def jvol_randomize(self, ds_entry):             # @todo: Consider: Should we bother doing mismatches / hallucinations for the numerics?
        if (vol := ds_entry["data"]["journal"]["volume"]):  # Not all references contain vol/iss data.
            vol = int(vol)
            ds_entry["data"]["journal"]["volume"] = random.choice([v for v in range(int(vol*.5), int(vol*1.5)) if v != vol]) # Arbitrary. Randomization range is the volume +/- half
        else:
            ds_entry["data"]["journal"]["volume"] = random.randint(0,500)
            print(f" ! empty vol in {ds_entry["id"]} {ds_entry["src_id"]}, setting to niave random: {ds_entry["data"]["journal"]["volume"]}")
            self._flag(ds_entry, "jvol_randomize")
        return ds_entry

    def jiss_randomize(self, ds_entry):
        if (iss := ds_entry["data"]["journal"]["issue"]):
            iss = int(iss)
            ds_entry["data"]["journal"]["issue"] = random.choice([i for i in range(int(iss*.5), int(iss*1.5)) if i != iss])
        else:
            # @todo: If we want to ensure that we create a database subset with vols and iss randomizations, we could return a None to signal.
            #        ALTERNATIVE would be to fail around it, and put some random number anyways.
            #ds_entry["data"]["journal"]["issue"] = random.choice(self._COMPONENTS["journal"])["issue"] # !! It must be that the same empties exist in the compset. SO, just do a random number.
            ds_entry["data"]["journal"]["issue"] = random.randint(0,1500)
            print(f" ! empty iss in {ds_entry["id"]} {ds_entry["src_id"]}, setting to niave random: {ds_entry["data"]["journal"]["issue"]}")

        self._flag(ds_entry, "jiss_randomize")
        return ds_entry

    # Could also perchance do a jissvol_mismatch (if one of our classifications implies it)

### JOURNAL PAGE NUMBERS

    def jpage_randomize(self, ds_entry): pass


    # Other possibilities: mismatch, nonesense_randomize (end < start)
    # If we do mismatches for these ones, that would make a big jALL_mismatch easy. Though it would be regardless, cause of compset structure. Whatever.

### JOURNAL PUBLICATION DATES

    def jpub_mismatch(self, ds_entry): pass
    def jpub_randomize(self, ds_entry): pass

### DIGITIAL PUBLICATION DATES

    def epub_mismatch(self, ds_entry): pass
    def epub_randomize(self, ds_entry): pass

### DOI

    def doi_typo(self, ds_entry): pass                  # @todo: Consider: If we do typo's on numerics, should they include fatfinger or only swap? The assumption is that fatfinger typos are too rare in this case (letters in a number would be seen and fixed).
    # ^ add one to each side or wu?
    def doi_mismatch_prefix(self, ds_entry): pass
    def doi_mismatch_suffix(self, ds_entry): pass
    def doi_randomize_prefix(self, ds_entry): pass
    def doi_randomize_suffix(self, ds_entry): pass

### PMIDS / PMCIDS

    def pmid_typo(self, ds_entry): pass
    def pmid_mismatch(self, ds_entry): pass
    def pmid_randomize(self, ds_entry): pass
    def pmcid_typo(self, ds_entry): pass
    def pmcid_mismatch(self, ds_entry): pass
    def pmcid_randomize(self, ds_entry): pass


# @todo: Consider: Should we just blanket each element with the same boilerplate mutation methods, even when it might not make complete sense? (such as mismatches on vol/iss, or hallucinating page numbers?)


# @todo: Consider: What about mutations which work on the final format itself? Like swaping a full journal name with an abreviation or vice versa? 
#                  Is such an error to minute to test, will it make a difference?
#                  We could just set the flag. Then it would be the format baker's responsibility to read it and bake accordingly.
