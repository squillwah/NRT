
from copy import deepcopy
from enum import StrEnum, Enum
from tools.references.typos import Typofier
from tools.references.refdata import ReferenceComponent
import random

class MutationType(StrEnum):
    TYPO = "typo"
    MISMATCH = "mismatch"
    HALLUCINATION = "hallucination"
    SHUFFLE = "shuffle"
    OMISSION = "omission"

class SeverityClass(float, Enum):
    NONE = 0.0
    ACCEPTABLE = 0.1        # For acceptable omissions? Like no PMCID, PMID, DOI...
    MINOR_ERROR = 0.33          # Slight errors, indicative of human style mistakes. Typos, small omissions.
    AMBIGUOUS_ERROR = 0.66      # More severe errors, cloud be human or machine. Author shuffle, small mismatches, larger omissions.
    MAJOR_ERROR = 1.0           # Most severe errors, definitively machinistic. Hallucinations, large mismatches, large omissions.
    #HUMAN_ERROR = 0.25
    #AMBIGUOUS_ERROR = .5
    #MAJOR_ERROR = .75
    #FAKE = 1.0

# @TODO Set dsentry severity initializers to NONE not REAL. Also make sure to check zeros when averaging...
# Thinking, more precises defintition. Also flipped it so 0 is no severe (no error), 1 is FAKE (error means it is no doubt hallucinated).

# Enum and utility aliases
C, M, S, T = ReferenceComponent, MutationType, SeverityClass, Typofier

# Scores are in two parts:
#  - Valid/Invalid (True if it's original, False if it's a mutated component)
#  - Arbitary Severity (A number in a range (or class alternatively) denoting our own classification of severity for a bad component)
#
# The score is applied to single components and the entire references.

# Class of methods to mutate dataset entries using ref_mutator functions.
class EntryMutator:

    # Mutation flags. Composed into a 'mutation code'. Unique bits describe exactly which modifications were performed on a dsentry. Not all mutations are combinable (overwrites). Also, be wary in the setting flags. A wrongly set flag will not reveal itself.

#    _MUT_BITFLAG = {}   # Map to the unique bit identifier of all defined mutations. Holdover from before constants. Bitcode works fine, don't care enough to change into new conventions.
#    _MUT_SEVERITY = {}   # Map to the suggested confidence value of all defined mutations.
#    _MUT_LABEL = {} # Human readable convenience labels for each bit identifier.
   
   # @ this is kind of like the 'weight' stuff with scoring, but applied to how much (thing being wrong) tarnishes the "validity" of a reference.
                                                                                                                                                                   
  # Right now all typos are .5 confidence, aka ambiguous on the generated -> authentic scale (invalid -> valid?).
   # We could have it change depending on element, perhaps author typos are less suspect, so a confidence of .75 instead?  @TODO fine tune
                                                                                                                                                                   
   # @todo we REALLY need to add the 'missing component' thing. Maybe. That would give reason for more variety in the weighting (not just .5 typos and 0 all else)
                                                                                                                                                                   
   # @ consider, when would it be above .5? Never really, cause we know it's been modified. Above .5 would incentivize confidence in the wrong answer... Right?
   # How are we going to compare their scores against this? Will it just be closeness, or does the funny business around the .5 interfere with that?
                                                                                                                                                                   
   # @TODO Reconsile the split DOI prefix/suffix mutation inconsistency.

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
        C.PUBLICATION_DATE: [                       # @TODO If we put in a check before applying a mutation (if entry["data"]["pub"] == none), that wouldn't work... Has_component should work right? One rule should be: don't apply omissions if has_component, and don't apply any other errors if has omission? How might that effect the dataset in an unexpected way?
            (M.HALLUCINATION,   S.MAJOR_ERROR),
            (M.OMISSION,        S.AMBIGUOUS_ERROR)
        ],                                                                    
        C.PMCID: [ 
            (M.TYPO,            S.MINOR_ERROR), 
            (M.MISMATCH,        S.MAJOR_ERROR), 
            (M.HALLUCINATION,   S.MAJOR_ERROR),
            (M.OMISSION,        S.MINOR_ERROR)      # Or should it be NONE? Not all references have PMCIDs... But that's handled elsewhere right? It is not included in the average if the original refdata was missing a PMCID, but it is included if it was ommitted. But! All our references have pmcids, so they're all included. The problem is that none of the references include the PMCID... so they're all going to have this error applied. If we set this error as a NONE severity, then what others should we set as NONE?
        ],                                          # If we set them as NONE, then they'll still be included in the average, and thus bias the average less severe. It should just not be included in the average. Should we have a 'don't include these components in average when ommitted' list? Or is that too specific. Is all of this stupid?
        C.PMID: [                                   # Could instead have another SeverityClass with low severity (.1 or .01) which represents these omissions...
            (M.TYPO,            S.MINOR_ERROR),
            (M.MISMATCH,        S.MAJOR_ERROR),
            (M.HALLUCINATION,   S.MAJOR_ERROR),
            (M.OMISSION,        S.MINOR_ERROR),     # S.ACCEPTABLE ?
        ],
        C.DOI: [ 
            (M.TYPO,            S.AMBIGUOUS_ERROR), 
            (M.MISMATCH,        S.MAJOR_ERROR), 
            (M.HALLUCINATION,   S.MAJOR_ERROR), 
            (M.OMISSION,        S.MINOR_ERROR)
        ] #"url_abstract":     ("typo", "mismatch", "hallucinate"), #"url_direct":       ("typo", "mismatch", "hallucinate"),
        # @TODO Still need those missing mutations. Would add complexity to the classfying.
    }

    # Construct static maps (mutations, bits, severities, functions)
    bit = 1
    for comp, muts in _MUTATION_DEFINES.items():
        _MUTATIONS[comp] = [m[0] for m in muts] # List of MutationTypes
        _MUTATION_SEVERITIES[comp], _MUTATION_BITFLAGS[comp], _MUTATION_DISPATCH[comp] = {}, {}, {}
        for (mut, severity) in muts:
            _MUTATION_SEVERITIES[comp][mut], _MUTATION_BITFLAGS[comp][mut] _MUTATION_DISPATCH[comp][mut], = severity, bit, None
            _CONVENIENCE_LABELS[bit] = f"{comp}::{mut}"
            bit = bit << 1
    del bit

    def __init__(self, *, component_set, h_titles, h_authors, h_journals, rand_year_range):
        # Resources for hallucination and mismatch mutations
        self._COMPONENTS = component_set            # Alternatively, if we think a hallucination sample for every component is a good idea:
        self._FAKE_TITLES = h_titles                # self._REAL_COMPONENTS
        self._FAKE_AUTHORS = h_authors              # self._FAKE_COMPONENTS
        self._FAKE_JOURNALS = h_journals            # The issue is, how fake can a date, DOI, or PMCID get? Fake enough to warrant that?
        self._RAND_YEAR_RANGE = (rand_year_range[0], rand_year_range[1])

# -------------------
# Helpers and Utility
# -------------------

    # Called after adding mutations. Sets mutation flags, adjusts component scores.
    @classmethod
    def _flag(cls, ds_entry, component, mutation):
        ds_entry["mut_code"] = ds_entry["mut_code"] | cls._MUTATION_BITFLAGS[component][mutation]
        
        # Flag the component as EXISTING or NOT EXISTING depending on mutation type:
        if mutation in (M.HALLUCINATION, M.MISMATCH): ds_entry["has_component"][component] = True      # @TODO Bring in gabe's omission stuff, then do the ANDing with reference specific component data in the bake.
        #elif mutation in (M.OMISSION): ds_entry["data"]["_meta"]["has_component"][component] = False
        
        # Lower or introduce score + severity class 
        #print(ds_entry["scores"]["component"][component])
        if not ds_entry["mut_severity"]["component"][component] or ds_entry["mut_severity"]["component"][component][1] > cls._MUTATION_SEVERITIES[component][mutation]:
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

    def author_typo(self, ds_entry):
        # For no good reason, author typo logic is different from T.typofy().
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
        self._flag(ds_entry, C.AUTHORS, M.TYPO)
        return ds_entry # Note: Reference returns are for convenience. They are not copies.

    def author_shuffle(self, ds_entry):
        random.shuffle(ds_entry["data"]["authors"])
        self._flag(ds_entry, C.AUTHORS, M.SHUFFLE)
        return ds_entry

    def author_mismatch(self, ds_entry):
        ds_entry["data"]["authors"] = self._randcopy(self._COMPONENTS["authors"])
        self._flag(ds_entry, C.AUTHORS, M.MISMATCH)
        return ds_entry

    def author_hallucinate(self, ds_entry):
        #ds_entry["data"]["authors"] = self._randcopy(self._FAKE_AUTHORS)    # It needs to be a list of fake authors.
        print(len(self._FAKE_AUTHORS))
        print(len(ds_entry["data"]["authors"]))
        print(ds_entry["data"]["pmcid"])
        # A random sample of authors, from 1 to len(authors)+5 < len(fake_authors)
        l1, l2 = len(ds_entry["data"]["authors"]) + 5, len(self._FAKE_AUTHORS)
        ds_entry["data"]["authors"] = deepcopy(random.sample(self._FAKE_AUTHORS, random.randint(1, l1 if l1 < l2 else l2)))
        self._flag(ds_entry, C.AUTHORS, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.AUTHORS][M.TYPO] = author_typo
    _MUTATION_DISPATCH[C.AUTHORS][M.SHUFFLE] = author_shuffle
    _MUTATION_DISPATCH[C.AUTHORS][M.MISMATCH] = author_mismatch
    _MUTATION_DISPATCH[C.AUTHORS][M.HALLUCINATION] = author_hallucinate

    def title_typo(self, ds_entry):
        ds_entry["data"]["title"] = T.typofy(ds_entry["data"]["title"])
        self._flag(ds_entry, C.TITLE, M.TYPO)
        return ds_entry
    
    def title_mismatch(self, ds_entry):
        #RM.set_title(ds_entry["data"], random.choice(self._COMPONENTS["title"]))   # Screw the ref_mutator shit
        ds_entry["data"]["title"] = self._randcopy(self._COMPONENTS["title"])
        self._flag(ds_entry, C.TITLE, M.MISMATCH)
        return ds_entry
    
    def title_hallucinate(self, ds_entry):
        #RM.set_title(ds_entry["data"], random.choice(self._FAKE_TITLES))
        ds_entry["data"]["title"] = self._randcopy(self._FAKE_TITLES)
        self._flag(ds_entry, C.TITLE, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.TITLE][M.TYPO] = title_typo
    _MUTATION_DISPATCH[C.TITLE][M.MISMATCH] = title_mismatch
    _MUTATION_DISPATCH[C.TITLE][M.HALLUCINATION] = title_hallucinate

# @todo: Think about: Should we be bothering with replacing each journal element like this, or should we just mismatch the whole thing together (name, date, volume, iss, pages)?

    def jname_typo(self, ds_entry):
        ds_entry["data"]["journal"]["name"]["short"] = T.typofy(ds_entry["data"]["journal"]["name"]["short"])
        ds_entry["data"]["journal"]["name"]["full"] = T.typofy(ds_entry["data"]["journal"]["name"]["full"])
        self._flag(ds_entry, C.JOURNAL_NAME, M.TYPO)
        return ds_entry
    def jname_mismatch(self, ds_entry):
        ds_entry["data"]["journal"]["name"] = self._randcopy([jname for jname in self._COMPONENTS["sets"]["journal_name"] if jname != ds_entry["data"]["journal"]["name"]])
        self._flag(ds_entry, C.JOURNAL_NAME, M.MISMATCH)
        return ds_entry
    def jname_hallucinate(self, ds_entry):
        ds_entry["data"]["journal"]["name"] = self._randcopy(self._FAKE_JOURNALS)    # @todo: !! Make sure the fake_journal source contains both full and short names, and that the file is parsed into the proper dict format!
        self._flag(ds_entry, C.JOURNAL_NAME, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.JOURNAL_NAME][M.TYPO] = jname_typo
    _MUTATION_DISPATCH[C.JOURNAL_NAME][M.MISMATCH] = jname_mismatch
    _MUTATION_DISPATCH[C.JOURNAL_NAME][M.HALLUCINATION] = jname_hallucinate

    def jvol_hallucinate(self, ds_entry):             # @todo: Consider: Should we bother doing mismatches / hallucinations for the numerics?
        if (vol := ds_entry["data"]["journal"]["volume"]):  # Not all references contain vol/iss data.
            vol = int(vol)
            ds_entry["data"]["journal"]["volume"] = random.choice([v for v in range(int(vol*.5), int(vol*1.5)) if v != vol]) # Arbitrary. Randomization range is the volume +/- half
        else:
            ds_entry["data"]["journal"]["volume"] = random.randint(0,500)
            print(f" ! empty vol in {ds_entry["id"]} {ds_entry["id_source"]}, setting to niave random: {ds_entry["data"]["journal"]["volume"]}")
        self._flag(ds_entry, C.JOURNAL_VOLUME, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.JOURNAL_VOLUME][M.HALLUCINATION] = jvol_hallucinate

    def jiss_hallucinate(self, ds_entry):
        if (iss := ds_entry["data"]["journal"]["issue"]):
            iss = int(iss)
            ds_entry["data"]["journal"]["issue"] = random.choice([i for i in range(int(iss*.5), int(iss*1.5)) if i != iss])
        else:
            # @todo: If we want to ensure that we create a database subset with vols and iss randomizations, we could return a None to signal.
            #        ALTERNATIVE would be to fail around it, and put some random number anyways.
            #ds_entry["data"]["journal"]["issue"] = random.choice(self._COMPONENTS["journal"])["issue"] # !! It must be that the same empties exist in the compset. SO, just do a random number.
            ds_entry["data"]["journal"]["issue"] = random.randint(0,1500)
            print(f" ! empty iss in {ds_entry["id"]} {ds_entry["id_source"]}, setting to niave random: {ds_entry["data"]["journal"]["issue"]}")
        self._flag(ds_entry, C.JOURNAL_ISSUE, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.JOURNAL_ISSUE][M.HALLUCINATION] = jiss_hallucinate

    # Could also perchance do a jissvol_mismatch (if one of our classifications implies it)

    def jpage_hallucinate(self, ds_entry):
        spage = random.randint(23, 1184)    # Completely arbitrary randomness.
        length = random.randint(3, 51)
        ds_entry["data"]["journal"]["page"]["start"] = spage
        ds_entry["data"]["journal"]["page"]["end"] = spage+length
        self._flag(ds_entry, C.JOURNAL_PAGE, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.JOURNAL_PAGE][M.HALLUCINATION] = jpage_hallucinate

    # Other possibilities: mismatch, nonesense_randomize (end < start)
    # If we do mismatches for these ones, that would make a big jALL_mismatch easy. Though it would be regardless, cause of compset structure. Whatever.

    # @todo still
    # elocator mismatch, randomize, typo? For typo, what about off by one and swaps?
    # URL typo, mismatch, randomize?
    def elocator_mismatch(self, ds_entry):  # @Consider: What about when an article doesn't have an elocator (or any other thing), should the mismatch still occur?
        ds_entry["data"]["journal"]["elocator"] = self._randcopy([eloc for eloc in self._COMPONENTS["sets"]["journal_elocator"] if eloc != ds_entry["data"]["journal"]["elocator"]])
        self._flag(ds_entry, C.ELOCATOR, M.MISMATCH)
        return ds_entry

    def elocator_hallucinate(self, ds_entry):
        num = str(random.randint(1, 999999))
        ds_entry["data"]["journal"]["elocator"] = "e"+"0"*(6-len(num))+num
        self._flag(ds_entry, C.ELOCATOR, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.ELOCATOR][M.MISMATCH] = elocator_mismatch
    _MUTATION_DISPATCH[C.ELOCATOR][M.HALLUCINATION] = elocator_hallucinate

    def pubs_hallucinate(self, ds_entry, *, y=True, m=True, d=True):                           # @Consider: Or should both pub and epub be done at once, with only a few days between?
        if y or m or d:
            pub = ds_entry["data"]["pub"]
            epub = ds_entry["data"]["epub"]
            if y:
                pub["y"] = random.randint(*self._RAND_YEAR_RANGE)
                epub["y"] = pub["y"]
            if m:
                pub["m"] = random.randint(1, 12)
                epub["m"] = pub["m"] + random.randint((pub["m"] > 1)*-1, (pub["m"] < 12)*1) # Sometimes offset epub month by 1.
            if d:
                pub["d"] = random.randint(1, 31)  # Hmmm
                epub["d"] = pub["d"] + random.randint((pub["d"] > 5)*-5, (pub["m"] < 27)*5) # Sometimes offset epub day by up to 5.
            self._flag(ds_entry, C.PUBLICATION_DATE, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.PUBLICATION_DATE][M.HALLUCINATION] = pubs_hallucinate

#    def pub_mismatch(self, ds_entry):
#    def epub_mismatch(self, ds_entry): pass
#    def epub_randomize(self, ds_entry, *, y=True, m=True, d=True):
#        if y: ds_entry["data"]["epub"]["y"] = random.randint(*self._RAND_YEAR_RANGE)
#        if m: ds_entry["data"]["epub"]["m"] = random.randint(1, 12)
#        if d: ds_entry["data"]["epub"]["d"] = random.randint(1, 31)
#        if y or m or d: self._flag(ds_entry, "epub_randomize")
#        return ds_entry

#    def _doi_mismatch_prefix(self, ds_entry):
#        ds_entry["data"]["doi"]["prefix"] = self._randcopy([p for p in self._COMPONENTS["sets"]["doi_prefix"] if p != ds_entry["data"]["doi"]["prefix"]])
#        #self._flag(ds_entry, "doi_mismatch_prefix")
#        self._flag(ds_entry, C.DOI, M.MISMATCH)         # Prefix and suffix used to be seperate, now aren't. Should they?
#        return ds_entry
#    def _doi_mismatch_suffix(self, ds_entry):
#        ds_entry["data"]["doi"]["suffix"] = self._randcopy([s for s in self._COMPONENTS["sets"]["doi_suffix"] if s != ds_entry["data"]["doi"]["suffix"]])
#        #self._flag(ds_entry, "doi_mismatch_suffix")
#        self._flag(ds_entry, C.DOI, M.MISMATCH)
#        return ds_entry
#    def _doi_hallucinate_prefix(self, ds_entry):
#        # 10.random1000->9999 + .random0->10or100or1000 (0-2x)
#        ds_entry["data"]["doi"]["prefix"] = ".".join(["10", str(random.randint(1000, 9999))] + [str(random.randint(0, 10**random.randint(1, 3))) for i in range(random.randint(0,2))])
#        #self._flag(ds_entry, "doi_hallucinate_prefix")
#        self._flag(ds_entry, C.DOI, M.HALLUCINATION)
#        return ds_entry
#    def _doi_hallucinate_suffix(self, ds_entry):
#        # 1-3 groups of 3 to 8 random numbers and letters
#        ds_entry["data"]["doi"]["suffix"] = "-".join(["".join([random.choice("abcdefghijklmnopqrstuvwxyz,./12345678900987654321") for i in range(random.randint(3, 8))]) for i in range(random.randint(1, 3))])
#        #self._flag(ds_entry, "doi_hallucinate_suffix")
#        self._flag(ds_entry, C.DOI, M.HALLUCINATION)
#        return ds_entry
   
    def doi_typo(self, ds_entry):                       # @todo: Consider: If we do typo's on numerics, should they include fatfinger or only swap? The assumption is that fatfinger typos are too rare in this case (letters in a number would be seen and fixed).
        doi = ds_entry["data"]["doi"]
        doi["prefix"] = T.typo_swapletter(doi["prefix"], random.choice([i for i, char in enumerate(doi["prefix"]) if char != "0"])) # Swap one char in the prefix (not zeros).
        doi["suffix"] = T.typofy(doi["suffix"]) # Just run the standard typo procedure on the suffix.
        self._flag(ds_entry, C.DOI, M.TYPO)
        return ds_entry

   def _doi_mismatch(self, ds_entry):
        ds_entry["data"]["doi"]["prefix"] = self._randcopy([p for p in self._COMPONENTS["sets"]["doi_prefix"] if p != ds_entry["data"]["doi"]["prefix"]])
        ds_entry["data"]["doi"]["suffix"] = self._randcopy([s for s in self._COMPONENTS["sets"]["doi_suffix"] if s != ds_entry["data"]["doi"]["suffix"]])
        self._flag(ds_entry, C.DOI, M.MISMATCH)
        return ds_entry
        
    def _doi_hallucinate(self, ds_entry):
        # 10.random1000->9999 + .random0->10or100or1000 (0-2x)
        ds_entry["data"]["doi"]["prefix"] = ".".join(["10", str(random.randint(1000, 9999))] + [str(random.randint(0, 10**random.randint(1, 3))) for i in range(random.randint(0,2))])
        # 1-3 groups of 3 to 8 random numbers and letters
        ds_entry["data"]["doi"]["suffix"] = "-".join(["".join([random.choice("abcdefghijklmnopqrstuvwxyz,./12345678900987654321") for i in range(random.randint(3, 8))]) for i in range(random.randint(1, 3))])
        self._flag(ds_entry, C.DOI, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.DOI][M.TYPO] = doi_typo
    _MUTATION_DISPATCH[C.DOI][M.MISMATCH] = doi_mismatch
    _MUTATION_DISPATCH[C.DOI][M.HALLUCINATION] = doi_hallucinate

    # ...       @todo something with the URLs???        ### URLS
    
    def _pmid_typo(self, ds_entry):
        # Only one typo.
        # 50/50 chance between positional swap or ++/-- error.
        ID = ds_entry["data"]["pmid"]
        li = random.randrange(0, len(ID))
        if random.random() <= .5:
            ID = T.typo_swapletter(ID, li)
        else:
            num = int(ID[li])
            if num == 9: num = num - 1
            elif num == 0: num = num + 1
            else: num = num + random.choice([-1,1])
            ID = ID[0:li]+str(num)+ID[li+1:] if li < len(ID)-1 else ID[0:li]+str(num)
        ds_entry["data"]["pmid"] = ID
        self._flag(ds_entry, C.PMID, M.TYPO)
        return ds_entry

    def _pmid_mismatch(self, ds_entry):
        ds_entry["data"]["pmid"] = self._randcopy([ID for ID in self._COMPONENTS["pmid"] if ID != ds_entry["data"]["pmid"]])
        self._flag(ds_entry, C.PMID, M.MISMATCH)
        return ds_entry

    def _pmid_hallucinate(self, ds_entry):
        ds_entry["data"]["pmid"] = str(random.randint(1, 999999999)) # Up to 9 digits.
        self._flag(ds_entry, C.PMID, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.PMID][M.TYPO] = pmid_typo
    _MUTATION_DISPATCH[C.PMID][M.MISMATCH] = pmid_mismatch
    _MUTATION_DISPATCH[C.PMID][M.HALLUCINATION] = pmid_hallucinate

    # Basically all exact same.
    def _pmcid_typo(self, ds_entry):
        ID = ds_entry["data"]["pmcid"]
        li = random.randrange(3, len(ID))   # Avoid PMC prefix
        if random.random() <= .5:
            ID = T.typo_swapletter(ID, li)
        else:
            num = int(ID[li])
            if num == 9: num = num - 1
            elif num == 0: num = num + 1
            else: num = num + random.choice([-1,1])
            ID = ID[0:li]+str(num)+ID[li+1:] if li < len(ID)-1 else ID[0:li]+str(num)
        ds_entry["data"]["pmcid"] = ID
        self._flag(ds_entry, C.PMCID, M.TYPO)
        return ds_entry
    
    def _pmcid_mismatch(self, ds_entry):
        ds_entry["data"]["pmcid"] = self._randcopy([ID for ID in self._COMPONENTS["pmcid"] if ID != ds_entry["data"]["pmcid"]])
        self._flag(ds_entry, C.PMCID, M.MISMATCH)
        return ds_entry

    def _pmcid_hallucinate(self, ds_entry):
        ds_entry["data"]["pmcid"] = "PMC"+str(random.randint(1, 99999999)) # Up to 8 digits. Plus PMC prefix.
        self._flag(ds_entry, C.PMCID, M.HALLUCINATION)
        return ds_entry
    
    _MUTATION_DISPATCH[C.PMCID][M.TYPO] = pmcid_typo
    _MUTATION_DISPATCH[C.PMCID][M.MISMATCH] = pmcid_mismatch
    _MUTATION_DISPATCH[C.PMCID][M.HALLUCINATION] = pmcid_hallucinate

# ---------
# Interface
# ---------

    # Apply a mutation.
    def mutate(self, dsentry, component, mutation): 
        return self._MUTATION_DISPATCH[component][mutation](dsentry)    # Return is for convenience. Entries are modified in place.
    
    # See mutations applied to an entry.
    @classmethod
    def explain_mutcode(cls, code):
        return [cls._CONVENIENCE_LABELS[bit] for bit in cls._CONVENIENCE_LABELS if (code & bit)]
    
    # Return dict of compatible mutations for all component types.
    @classmethod
    def get_mutations(cls):
        return cls._MUTATIONS
   
    # Return list of compatible mutations for given component type.
    @classmethod
    def get_mutations(cls, component):
        return cls._MUTATIONS[component]

# @todo: Consider: Should we just blanket each element with the same boilerplate mutation methods, even when it might not make complete sense? (such as mismatches on vol/iss, or hallucinating page numbers?)


# @todo: Consider: What about mutations which work on the final format itself? Like swaping a full journal name with an abreviation or vice versa? 
#                  Is such an error to minute to test, will it make a difference?
#                  We could just set the flag. Then it would be the format baker's responsibility to read it and bake accordingly.




    # Mutation level. Or, the classification of a reference based on the sum of it's mutations.
    # Differentiates between ambigious "human-esque" reference mistakes, and undeniably "chatbot-esque" hallucinations.


# @Consider: One thing with the score totalling, is journal_page/journal_volume vs elocator can change scores. When one substitutes the other in the ref, even though both are valid. Because page + vol are 2 values, the 'weight' of them combined is heavier than elocator, even though they're subsituting each other.



# @CONSIDER: Sometimes the true/false and the confidence score wont line up. Should the True/False be more of a "was this modified thing" or stay the same as the conf. Probably stay the same. Idk just think about it. There's something there.
# @CONSIDER !! What about adding hallucinated/mismatch components to references which never had one in the first place?
#  The question is: Should we only mutate a component when it already exists (refdataCOMPONENTS = True), or should we always mutate?
#  how address in scoring?
#  should we keep list of modified components?
#  we have comp score list at init already, with Trues and Nones when no component.
#  so, we set that value during the check. scores modified in place during mutation
#  then if we do or dont want mutating of absent components, we just disable it on the None check instead of creating new.

            #""combined": [True, 1.0],        # @ These two are where some kind of weight would come in, but right now they don't matter at all.
            #""byformat": {"ama": None},                                                                              # @TODO {form: None for form in FormatStyles}. Different holistic scores per format addresses the issue of absent components bias.
            #""component": {comp: ([True, 1.0] if rd["_meta"]["has_component"][comp] else None) for comp in ReferenceComponent}   # @RECONSIDER: The holistic score totalling nonsense is convoluted and an overcomplication.


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
