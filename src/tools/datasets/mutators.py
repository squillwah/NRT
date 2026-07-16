
from copy import deepcopy
from enum import StrEnum, Enum
from tools.references.typos import Typofier
from tools.references.refdata import ReferenceComponent
from tools.help import log
import random

class MutationType(StrEnum):
    TYPO = "typo"
    MISMATCH = "mismatch"
    HALLUCINATION = "hallucination"
    SHUFFLE = "shuffle"
    OMISSION = "omission"

# Severity goes kind of exponential?
class SeverityClass(float, Enum):
    NONE = 0.0
    COMMON_VARIATION = 0.001  # For acceptable omissions? Like no PMCID, PMID, DOI...
    MINOR_ERROR = 0.01          # Slight errors, indicative of human style mistakes. Typos, small omissions.
    AMBIGUOUS_ERROR = 0.1      # More severe errors, cloud be human or machine. Author shuffle, small mismatches, larger omissions.
    MAJOR_ERROR = 1.0           # Most severe errors, definitively machinistic. Hallucinations, large mismatches, large omissions.

C, M, S, T = ReferenceComponent, MutationType, SeverityClass, Typofier  # Enum and utility aliases

# Class of methods to mutate dataset entries.
class EntryMutator:
    
    # Supported mutations. Map of {ReferenceComponent: [<supported MutationType>, ...]}
    _MUTATIONS = {}
    # Severities of unique mutations. Map of {RC: {MT: <SeverityClass>, ...}, ...}
    _MUTATION_SEVERITIES = {}
    # Unique mutation bitflags / IDs + human readable labels. Map of {RC: {MT: 0b00, ...}, ...} + {0b00: <"label">}
    _MUTATION_BITFLAGS, _CONVENIENCE_LABELS = {}, {}
    # Map of {RC: {MT: <method reference>, ...}, ...}. For generalized calling. References are added below each function defintion.
    _MUTATION_DISPATCH = {}
    
    # Defines possible mutations per component type, arbitary severity associated with mutation.
    _MUTATION_DEFINES = {
        C.AUTHORS: [ 
            (M.TYPO,            S.MINOR_ERROR), 
            (M.MISMATCH,        S.MAJOR_ERROR), 
            (M.HALLUCINATION,   S.MAJOR_ERROR), 
            (M.SHUFFLE,         S.AMBIGUOUS_ERROR),
            (M.OMISSION,        S.MAJOR_ERROR)
        ],  
        C.TITLE: [ 
            (M.TYPO,            S.MINOR_ERROR), 
            (M.MISMATCH,        S.MAJOR_ERROR), 
            (M.HALLUCINATION,   S.MAJOR_ERROR), 
            (M.OMISSION,        S.AMBIGUOUS_ERROR)  # Some publishers include no title.
        ],
        C.JOURNAL_NAME: [ 
            (M.TYPO,            S.MINOR_ERROR), 
            (M.MISMATCH,        S.AMBIGUOUS_ERROR), 
            (M.HALLUCINATION,   S.MAJOR_ERROR),
            (M.OMISSION,        S.MAJOR_ERROR)
        ],                       
        C.JOURNAL_VOLUME: [ 
            (M.HALLUCINATION,   S.MAJOR_ERROR),
            (M.OMISSION,        S.AMBIGUOUS_ERROR)
        ],
        C.JOURNAL_ISSUE: [ 
            (M.HALLUCINATION,   S.MAJOR_ERROR),
            (M.OMISSION,        S.MINOR_ERROR)
        ],
        C.JOURNAL_PAGE: [ 
            (M.HALLUCINATION,   S.AMBIGUOUS_ERROR),
            (M.OMISSION,        S.MINOR_ERROR)
        ],                                                                      
        C.ELOCATOR: [ 
            (M.MISMATCH,        S.MAJOR_ERROR), 
            (M.HALLUCINATION,   S.MAJOR_ERROR),
            (M.OMISSION,        S.MINOR_ERROR)
        ],
        C.PUBLICATION_DATE: [                       # @TODO If we put in a check before applying a mutation (if entry["ref_data"]["pub"] == none), that wouldn't work... Has_component should work right? One rule should be: don't apply omissions if has_component, and don't apply any other errors if has omission? How might that effect the dataset in an unexpected way?
            (M.HALLUCINATION,   S.MAJOR_ERROR),
            (M.OMISSION,        S.AMBIGUOUS_ERROR)
        ],                                                                    
        C.PMCID: [ 
            (M.TYPO,            S.MINOR_ERROR), 
            (M.MISMATCH,        S.MAJOR_ERROR), 
            (M.HALLUCINATION,   S.MAJOR_ERROR),
            (M.OMISSION,        S.COMMON_VARIATION) # Or should it be NONE? Not all references have PMCIDs... But that's handled elsewhere right? It is not included in the average if the original refdata was missing a PMCID, but it is included if it was ommitted. But! All our references have pmcids, so they're all included. The problem is that none of the references include the PMCID... so they're all going to have this error applied. If we set this error as a NONE severity, then what others should we set as NONE?
        ],                                              # If we set them as NONE, then they'll still be included in the average, and thus bias the average less severe. It should just not be included in the average. Should we have a 'don't include these components in average when ommitted' list? Or is that too specific. Is all of this stupid?
        C.PMID: [                                       # Could instead have another SeverityClass with low severity (.1 or .01) which represents these omissions...
            (M.TYPO,            S.MINOR_ERROR),
            (M.MISMATCH,        S.MAJOR_ERROR),
            (M.HALLUCINATION,   S.MAJOR_ERROR),
            (M.OMISSION,        S.COMMON_VARIATION), # S.ACCEPTABLE ?
        ],
        C.DOI: [ 
            (M.TYPO,            S.AMBIGUOUS_ERROR), 
            (M.MISMATCH,        S.MAJOR_ERROR), 
            (M.HALLUCINATION,   S.MAJOR_ERROR), 
            (M.OMISSION,        S.COMMON_VARIATION)
        ]
    }

    # Construct static maps (mutations, bits, severities, functions)
    bit = 1
    for comp, muts in _MUTATION_DEFINES.items():
        _MUTATIONS[comp] = [m[0] for m in muts] # List of MutationTypes
        _MUTATION_SEVERITIES[comp], _MUTATION_BITFLAGS[comp], _MUTATION_DISPATCH[comp] = {}, {}, {}
        for (mut, severity) in muts:
            _MUTATION_SEVERITIES[comp][mut], _MUTATION_BITFLAGS[comp][mut], _MUTATION_DISPATCH[comp][mut], = severity, bit, None
            _CONVENIENCE_LABELS[bit] = f"{comp}::{mut}"
            bit = bit << 1
    del bit

    # Instanced resources for hallucination and mismatch mutations
    def __init__(self, *, component_set, h_titles, h_authors, h_journals, rand_year_range):
        self._COMPONENTS = component_set
        self._FAKE_TITLES = h_titles
        self._FAKE_AUTHORS = h_authors
        self._FAKE_JOURNALS = h_journals
        self._RAND_YEAR_RANGE = (rand_year_range[0], rand_year_range[1])

# -------------------
# Helpers and Utility
# -------------------

    # Called after adding mutations. Sets mutation flags, adjusts component scores.
    @classmethod
    def _flag(cls, ds_entry, component, mutation):
        ds_entry["mut_code"] = ds_entry["mut_code"] | cls._MUTATION_BITFLAGS[component][mutation]
        
        # If we've come this far (calling through mutate() dispatcher), then we should be guaranteed that the component does or did exist.
        # Flag the component as EXISTING or NOT EXISTING depending on mutation type:
        ds_entry["has_component"][component] = not (mutation == M.OMISSION)
        
        #if mutation in (M.HALLUCINATION, M.MISMATCH): ds_entry["has_component"][component] = True      # @TODO Bring in gabe's omission stuff, then do the ANDing with reference specific component data in the bake.
        #elif mutation in (M.OMISSION): ds_entry["ref_data"]["_meta"]["has_component"][component] = False
        
        # Lower or introduce score + severity class 
        #print(ds_entry["scores"]["component"][component])
        if not ds_entry["mut_severity"]["component"][component] or ds_entry["mut_severity"]["component"][component][1] < cls._MUTATION_SEVERITIES[component][mutation]:
            #print(ds_entry["scores"]["component"][component])
            ds_entry["mut_severity"]["component"][component] = (False, cls._MUTATION_SEVERITIES[component][mutation])
            #print(ds_entry["scores"]["component"][component])

    # Return deepcopy of random item from collection.
    @staticmethod
    def _randcopy(collection):
        return deepcopy(random.choice(collection))


# --------------------------
# Component Mutation Methods 
# --------------------------

    def _author_typo(self, ds_entry):
        # For no good reason, author typo logic is different from T.typofy().
        # As a completely arbitrary heuristic, let it be that:                                                          # This one? https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7546536
        #  - There is a 1/4 chance for a typo to appear in an author's name. 
        #  - Some considerations are made for appearing in the final formats:
        #    - Typos are added to both the last and first names simultaneously.
        #    - The first three authors are guaranteed to have at least one typo.
        #  - Compounding typo's follow the natural halving of the probability (2: 1/8, 3: 1/16, so on)
        #  - Fatfingers are twice as likely as swaps (moved into typofier.fatswap)
        TYPO_CHANCE = 1/3
        authors = ds_entry["ref_data"]["authors"]
        for author_i, name in enumerate(authors):
            first_three_guarantee = author_i > 2
            while random.random() <= TYPO_CHANCE or not first_three_guarantee:
                for part in name:
                    if name[part]: # Skip over empty names.
                        print(" ? ", name, part)
                        letter_i = random.choice([i for i, letter in enumerate(name[part])])
                        name[part] = T.fatswap(name[part], letter_i)
                first_three_guarantee = True
        return True

    def _author_shuffle(self, ds_entry):
        random.shuffle(ds_entry["ref_data"]["authors"])
        return True

    def _author_mismatch(self, ds_entry):
        ds_entry["ref_data"]["authors"] = self._randcopy(self._COMPONENTS["authors"])
        return True

    def _author_hallucination(self, ds_entry):
        # A random sample of authors, from 1 to len(authors)+5 < len(fake_authors)
        l1, l2 = len(ds_entry["ref_data"]["authors"]) + 5, len(self._FAKE_AUTHORS)
        ds_entry["ref_data"]["authors"] = deepcopy(random.sample(self._FAKE_AUTHORS, random.randint(1, l1 if l1 < l2 else l2)))
        return True

    def _author_omission(self, ds_entry):
        authors = ds_entry["ref_data"]["authors"]
        omittable = authors is not None and len(authors) > 0
        if omittable: ds_entry["ref_data"]["authors"] = None
        return omittable
    
    _MUTATION_DISPATCH[C.AUTHORS][M.TYPO] = _author_typo
    _MUTATION_DISPATCH[C.AUTHORS][M.SHUFFLE] = _author_shuffle
    _MUTATION_DISPATCH[C.AUTHORS][M.MISMATCH] = _author_mismatch
    _MUTATION_DISPATCH[C.AUTHORS][M.HALLUCINATION] = _author_hallucination
    _MUTATION_DISPATCH[C.AUTHORS][M.OMISSION] = _author_omission

    def _title_typo(self, ds_entry):
        ds_entry["ref_data"]["title"] = T.typofy(ds_entry["ref_data"]["title"])
        return True
    
    def _title_mismatch(self, ds_entry):
        ds_entry["ref_data"]["title"] = self._randcopy(self._COMPONENTS["title"])
        return True
    
    def _title_hallucination(self, ds_entry):
        ds_entry["ref_data"]["title"] = self._randcopy(self._FAKE_TITLES)
        return True
    
    def _title_omission(self, ds_entry):
        omittable = bool(ds_entry["ref_data"]["title"])
        if omittable: ds_entry["ref_data"]["title"] = None
        return omittable
    
    _MUTATION_DISPATCH[C.TITLE][M.TYPO] = _title_typo
    _MUTATION_DISPATCH[C.TITLE][M.MISMATCH] = _title_mismatch
    _MUTATION_DISPATCH[C.TITLE][M.HALLUCINATION] = _title_hallucination
    _MUTATION_DISPATCH[C.TITLE][M.OMISSION] = _title_omission

    def _journal_name_typo(self, ds_entry):
        ds_entry["ref_data"]["journal"]["name"]["short"] = T.typofy(ds_entry["ref_data"]["journal"]["name"]["short"])
        ds_entry["ref_data"]["journal"]["name"]["full"] = T.typofy(ds_entry["ref_data"]["journal"]["name"]["full"])
        return True
    
    def _journal_name_mismatch(self, ds_entry):
        ds_entry["ref_data"]["journal"]["name"] = self._randcopy([jname for jname in self._COMPONENTS["sets"]["journal_name"] if jname != ds_entry["ref_data"]["journal"]["name"]])
        return True
    
    def _journal_name_hallucination(self, ds_entry):
        ds_entry["ref_data"]["journal"]["name"] = self._randcopy(self._FAKE_JOURNALS)
        return True
    
    def _journal_name_omission(self, ds_entry):
        omittable = bool(ds_entry["ref_data"]["journal"]["name"])
        if omittable: ds_entry["ref_data"]["journal"]["name"] = None
        return omittable
    
    _MUTATION_DISPATCH[C.JOURNAL_NAME][M.TYPO] = _journal_name_typo
    _MUTATION_DISPATCH[C.JOURNAL_NAME][M.MISMATCH] = _journal_name_mismatch
    _MUTATION_DISPATCH[C.JOURNAL_NAME][M.HALLUCINATION] = _journal_name_hallucination
    _MUTATION_DISPATCH[C.JOURNAL_NAME][M.OMISSION] = _journal_name_omission

    def _journal_volume_hallucination(self, ds_entry):
        if (vol := ds_entry["ref_data"]["journal"]["volume"]):  # Not all references contain vol/iss data.
            vol = int(vol)
            ds_entry["ref_data"]["journal"]["volume"] = random.choice([v for v in range(int(vol*.5), int(vol*1.5)) if v != vol]) # Arbitrary. Randomization range is the volume +/- half
        else:
            ds_entry["ref_data"]["journal"]["volume"] = random.randint(0,500)
            print(f" ! empty vol in {ds_entry["id"]} {ds_entry["id_source"]}, setting to niave random: {ds_entry["ref_data"]["journal"]["volume"]}")
        return True
    
    def _journal_volume_omission(self, ds_entry):
        omittable = bool(ds_entry["ref_data"]["journal"]["volume"])
        if omittable: ds_entry["ref_data"]["journal"]["volume"] = None
        return omittable
    
    _MUTATION_DISPATCH[C.JOURNAL_VOLUME][M.HALLUCINATION] = _journal_volume_hallucination
    _MUTATION_DISPATCH[C.JOURNAL_VOLUME][M.OMISSION] = _journal_volume_omission

    def _jiss_hallucination(self, ds_entry):
        if (iss := ds_entry["ref_data"]["journal"]["issue"]):
            iss = int(iss)
            ds_entry["ref_data"]["journal"]["issue"] = random.choice([i for i in range(int(iss*.5), int(iss*1.5)) if i != iss])
        else:
            ds_entry["ref_data"]["journal"]["issue"] = random.randint(0,1500)
            print(f" ! empty iss in {ds_entry["id"]} {ds_entry["id_source"]}, setting to niave random: {ds_entry["ref_data"]["journal"]["issue"]}")
        return True
    
    def _jiss_omission(self, ds_entry):
        omittable = bool(ds_entry["ref_data"]["journal"]["issue"])
        if omittable: ds_entry["ref_data"]["journal"]["issue"] = None
        return omittable
    
    _MUTATION_DISPATCH[C.JOURNAL_ISSUE][M.HALLUCINATION] = _jiss_hallucination
    _MUTATION_DISPATCH[C.JOURNAL_ISSUE][M.OMISSION] = _jiss_omission

    def _journal_page_hallucination(self, ds_entry):
        spage = random.randint(23, 1184)    # Completely arbitrary randomness.
        length = random.randint(3, 51)
        ds_entry["ref_data"]["journal"]["page"]["start"] = spage
        ds_entry["ref_data"]["journal"]["page"]["end"] = spage+length
        return True
    
    def _journal_page_omission(self, ds_entry):
        page = ds_entry["ref_data"]["journal"]["page"] 
        omittable = page is not None and (bool(page["start"]) or bool(page["end"])) # Because page is a dict of two strings.
        if omittable: ds_entry["ref_data"]["journal"]["page"] = None
        return omittable
    
    _MUTATION_DISPATCH[C.JOURNAL_PAGE][M.HALLUCINATION] = _journal_page_hallucination
    _MUTATION_DISPATCH[C.JOURNAL_PAGE][M.OMISSION] = _journal_page_omission

    def _elocator_mismatch(self, ds_entry):
        ds_entry["ref_data"]["journal"]["elocator"] = self._randcopy([eloc for eloc in self._COMPONENTS["sets"]["journal_elocator"] if eloc != ds_entry["ref_data"]["journal"]["elocator"]])
        return True

    def _elocator_hallucination(self, ds_entry):
        num = str(random.randint(1, 999999))
        ds_entry["ref_data"]["journal"]["elocator"] = "e"+"0"*(6-len(num))+num
        return True
    
    def _elocator_omission(self, ds_entry):
        omittable = bool(ds_entry["ref_data"]["journal"]["elocator"])
        if omittable: ds_entry["ref_data"]["journal"]["elocator"] = None
        return omittable
    
    _MUTATION_DISPATCH[C.ELOCATOR][M.MISMATCH] = _elocator_mismatch
    _MUTATION_DISPATCH[C.ELOCATOR][M.HALLUCINATION] = _elocator_hallucination
    _MUTATION_DISPATCH[C.ELOCATOR][M.OMISSION] = _elocator_omission

    def _publication_date_hallucination(self, ds_entry, *, y=True, m=True, d=True):
        if y or m or d:
            pub = ds_entry["ref_data"]["pub"]
            epub = ds_entry["ref_data"]["epub"]
            if y:
                pub["y"] = random.randint(*self._RAND_YEAR_RANGE)
                epub["y"] = pub["y"]
            if m:
                pub["m"] = random.randint(1, 12)
                epub["m"] = pub["m"] + random.randint((pub["m"] > 1)*-1, (pub["m"] < 12)*1) # Sometimes offset epub month by 1.
            if d:
                pub["d"] = random.randint(1, 31)  # Hmmm
                epub["d"] = pub["d"] + random.randint((pub["d"] > 5)*-5, (pub["m"] < 27)*5) # Sometimes offset epub day by up to 5.
            return True
        return False

    def _publication_date_omission(self, ds_entry):
        omittable = bool(ds_entry["ref_data"]["pub"]) or bool(ds_entry["ref_data"]["epub"])
        if omittable:
            ds_entry["ref_data"]["pub"] = None      # Both pubs should really be under the same thing ...
            ds_entry["ref_data"]["epub"] = None
        return omittable
    
    _MUTATION_DISPATCH[C.PUBLICATION_DATE][M.HALLUCINATION] = _publication_date_hallucination
    _MUTATION_DISPATCH[C.PUBLICATION_DATE][M.OMISSION] = _publication_date_omission
   
    def _doi_typo(self, ds_entry):
        doi = ds_entry["ref_data"]["doi"]
        doi["prefix"] = T.typo_swapletter(doi["prefix"], random.choice([i for i, char in enumerate(doi["prefix"]) if char != "0"])) # Swap one char in the prefix (not zeros).
        doi["suffix"] = T.typofy(doi["suffix"]) # Just run the standard typo procedure on the suffix.
        return True

    # @TODO Better randomization of suffix vs prefix mismatching / hallucinating?

    def _doi_mismatch(self, ds_entry):
        ds_entry["ref_data"]["doi"]["prefix"] = self._randcopy([p for p in self._COMPONENTS["sets"]["doi_prefix"] if p != ds_entry["ref_data"]["doi"]["prefix"]])
        ds_entry["ref_data"]["doi"]["suffix"] = self._randcopy([s for s in self._COMPONENTS["sets"]["doi_suffix"] if s != ds_entry["ref_data"]["doi"]["suffix"]])
        return True
        
    def _doi_hallucination(self, ds_entry):
        # 10.random1000->9999 + .random0->10or100or1000 (0-2x)
        ds_entry["ref_data"]["doi"]["prefix"] = ".".join(["10", str(random.randint(1000, 9999))] + [str(random.randint(0, 10**random.randint(1, 3))) for i in range(random.randint(0,2))])
        # 1-3 groups of 3 to 8 random numbers and letters
        ds_entry["ref_data"]["doi"]["suffix"] = "-".join(["".join([random.choice("abcdefghijklmnopqrstuvwxyz,./12345678900987654321") for i in range(random.randint(3, 8))]) for i in range(random.randint(1, 3))])
        return True

    def _doi_omission(self, ds_entry):
        doi = ds_entry["ref_data"]["doi"]
        omittable = doi is not None and (bool(doi["prefix"]) or bool(doi["suffix"])) # Because DOI is a dictionary of two strings.
        if omittable: ds_entry["ref_data"]["doi"] = None
        return omittable
    
    _MUTATION_DISPATCH[C.DOI][M.TYPO] = _doi_typo
    _MUTATION_DISPATCH[C.DOI][M.MISMATCH] = _doi_mismatch
    _MUTATION_DISPATCH[C.DOI][M.HALLUCINATION] = _doi_hallucination
    _MUTATION_DISPATCH[C.DOI][M.OMISSION] = _doi_omission

    # ...       @todo something with the URLs???        ### URLS
    
    def _pmid_typo(self, ds_entry):
        # Only one typo.
        # 50/50 chance between positional swap or ++/-- error.
        ID = ds_entry["ref_data"]["pmid"]
        li = random.randrange(0, len(ID))
        if random.random() <= .5:
            ID = T.typo_swapletter(ID, li)
        else:
            num = int(ID[li])
            if num == 9: num = num - 1
            elif num == 0: num = num + 1
            else: num = num + random.choice([-1,1])
            ID = ID[0:li]+str(num)+ID[li+1:] if li < len(ID)-1 else ID[0:li]+str(num)
        ds_entry["ref_data"]["pmid"] = ID
        return True

    def _pmid_mismatch(self, ds_entry):
        ds_entry["ref_data"]["pmid"] = self._randcopy([ID for ID in self._COMPONENTS["pmid"] if ID != ds_entry["ref_data"]["pmid"]])
        return True

    def _pmid_hallucination(self, ds_entry):
        ds_entry["ref_data"]["pmid"] = str(random.randint(1, 999999999)) # Up to 9 digits.
        return True

    def _pmid_omission(self, ds_entry):
        omittable = bool(ds_entry["ref_data"]["pmid"])
        if omittable: ds_entry["ref_data"]["pmid"] = None
        return True
    
    _MUTATION_DISPATCH[C.PMID][M.TYPO] = _pmid_typo
    _MUTATION_DISPATCH[C.PMID][M.MISMATCH] = _pmid_mismatch
    _MUTATION_DISPATCH[C.PMID][M.HALLUCINATION] = _pmid_hallucination
    _MUTATION_DISPATCH[C.PMID][M.OMISSION] = _pmid_omission

    # Basically all exact same.
    def _pmcid_typo(self, ds_entry):
        ID = ds_entry["ref_data"]["pmcid"]
        li = random.randrange(3, len(ID))   # Avoid PMC prefix
        if random.random() <= .5:
            ID = T.typo_swapletter(ID, li)
        else:
            num = int(ID[li])
            if num == 9: num = num - 1
            elif num == 0: num = num + 1
            else: num = num + random.choice([-1,1])
            ID = ID[0:li]+str(num)+ID[li+1:] if li < len(ID)-1 else ID[0:li]+str(num)
        ds_entry["ref_data"]["pmcid"] = ID
        return True
    
    def _pmcid_mismatch(self, ds_entry):
        ds_entry["ref_data"]["pmcid"] = self._randcopy([ID for ID in self._COMPONENTS["pmcid"] if ID != ds_entry["ref_data"]["pmcid"]])
        return True

    def _pmcid_hallucination(self, ds_entry):
        ds_entry["ref_data"]["pmcid"] = "PMC"+str(random.randint(1, 99999999)) # Up to 8 digits. Plus PMC prefix.
        return True
    
    def _pmcid_omission(self, ds_entry):
        omittable = bool(ds_entry["ref_data"]["pmcid"])
        if omittable: ds_entry["ref_data"]["pmcid"] = None    # Doing none checks on data before running omission. Refdata inits to either null or "" depending on component, but both null and "" are Falsey so it should work out always. Return false if omission couldn't apply (component already absent, nothing to omit).
        return omittable
    
    _MUTATION_DISPATCH[C.PMCID][M.TYPO] = _pmcid_typo
    _MUTATION_DISPATCH[C.PMCID][M.MISMATCH] = _pmcid_mismatch
    _MUTATION_DISPATCH[C.PMCID][M.HALLUCINATION] = _pmcid_hallucination
    _MUTATION_DISPATCH[C.PMCID][M.OMISSION] = _pmcid_omission

# ---------
# Interface
# ---------

    # Apply a mutation.
    def mutate(self, ds_entry, component, mutation): 
        # @TODO Add overwrite avoidance here (checking bitcode against bitflag[component][mutation]) or in the curves definition?
        # Should there be a check her to make sure typos don't get executed on absent components, or is that handled elsewhere? Or is it just such an edge case it will never happen...
        
#        if m is omission but component is not in set or already omitted, do not allow.
#        if m is typo or shuffle, but comonent is not in set or ommitted, do not allow
#        if m has a mutation applied that will be wiped by new one (typo wiped by mismatch), rerun the one being wiped to preserve accuracy.
        success = False 

        mutator = self._MUTATION_DISPATCH[component][mutation].__get__(self)
        success = mutator(ds_entry)
        if success: self._flag(ds_entry, component, mutation)
        return success
    
    # See mutations applied to an entry.
    # Really only used to make dataset JSONs more readable. (tbh the whole code thing is a holdover from before we had formal Enums)
    @classmethod
    def explain_mutcode(cls, code):
        return [cls._CONVENIENCE_LABELS[bit] for bit in cls._CONVENIENCE_LABELS if (code & bit)]
    
    # Return dict of compatible mutations for all component types.
    # Return list of compatible mutations for given component type.
    @classmethod
    def mutations(cls, component=None):
        return cls._MUTATIONS[component] if component else cls._MUTATIONS

    @classmethod
    def has_mutation(cls, ds_entry, component, mutation):
        return bool(ds_entry["mut_code"] & cls._MUTATION_BITFLAGS[component][mutation])
   

if __name__ == "__main__":
    import json
    print(json.dumps(EntryMutator._MUTATIONS, indent=2))
    print()
    print(json.dumps(EntryMutator._MUTATION_DISPATCH, indent=2, default=lambda x: str(x)))


"""
if __name__ == "__main__":
    import json
    import dstools.configurations as setconfig

    r = None
    with open("testrefs.json") as f: r = json.load(f)

    ds = make_dataset(r)
    bake_dataset(ds)
    print(json.dumps(ds, indent=4))


    DIR = "./reference_source"
    #with open(f"{DIR}/refdata.json", "r") as f: refdata_src = json.load(f)
    with open(f"testrefs.json", "r") as f: refdata_src = json.load(f)
    with open(f"{DIR}/compset.json", "r") as f: compset_src = json.load(f)
    with open(f"{DIR}/h_titles.txt", "r") as f: h_title_src = [line.strip() for line in f if line.strip()]
    with open(f"{DIR}/h_authors.txt", "r") as f:
        h_author_src = [{"l": "FAKEAUTH", "f": "FAKEAUTH"}]*200 #{ "l": name, "f": name for name in [line.strip() for line in f if line.strip()]} # Placeholder. Either parse by ', ' or have source generate a json of last and first.
    with open(f"{DIR}/h_journals.txt", "r") as f:
        h_journal_src = [{"full": "FAKEJOURN", "short": "FAKEJOURN"}]*200 #{ "full": name, "short": name for name in [line.strip() for line in f if line.strip()]} # Placeholder. Have the source be a JSON with {full, short}

    srcds = make_dataset(refdata_src*5)
    ds = { "source":        srcds[:100],
           "minor_mderror": srcds[100:200],
           "major_mderror": srcds[200:300],
           "plausible_fab": srcds[300:400],
           "human_review":  srcds[400:] }
    setconfig.init(h_titles=h_title_src, h_authors=h_author_src, h_journals=h_journal_src, component_set=compset_src, rand_year_range=(2024, 2026))
    setconfig.test_typos(ds["source"])
    bake_dataset(ds["source"])
    print(json.dumps(ds["source"], indent=2))
    #quit()


    setconfig.l1_metadata_error(ds["minor_mderror"])
    setconfig.l2_serious_metadata_error(ds["major_mderror"])
    setconfig.l3_plausible_fabricated(ds["plausible_fab"])
    setconfig.l4_needs_human_review(ds["human_review"])

    for label in ds: bake_dataset(ds[label])

    print(json.dumps(ds, indent=2))
"""
