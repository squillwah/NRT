
from copy import deepcopy
from reftools.typos import Typofier as T
from reftools.refdata import COMPONENT_LIST
#import reftools.ref_formatters as RB
import reftools.formats as F
import random



# @todo
#
#   Add other levels of flaggin
#   Mutcode_verbose (current)
#   Mutcode_gist    (flag whenever individual element is modified, so just author, title, journal, etc...)
#   Error_class     (flags class of entry)
#     - Subtle mutations (like typo, abreviation, stuff humans could make) will tip this over from 'real' into 'ambiguous'
#     - More egregious mutations (hallucinations, swaps) will flip it all the way into 'generated'.
#   
#     - What other classifications could exist, other than those three? They'd need to be distinct, orthogonal.
#
#     - This will be used in the grid / final data determination. It's the thing to compare against, the model's outputs, to evaluate their PERFORMANCE at detecting.
#       - is it too abstract/bespoke of classifcation? We should make sure it isn't/doesn't become. Keep it simple, broad, and distinct.
#

# After meeting (friday 07-03)
# ignoring / discounting results for components in references where they're absent. But having that missing ocmponent be evaluated is still valuable.
# two experiments, one with schema trimming and other without. This shows robustness of model, if absent components make it tend toward negative evaluation even when it shouldn't (like few references have PMCIDs, but nemotron marked it down cause of it missing wherase deepseek did true .5 vs .5)
#   different models evaluated absent components in different ways, effecting its weight toward them being absent. bringing total down or up. ROBUSTness?
#   making it 'fair' (schema trimming) vs not making life any easier for llms (full schema, let it hurt itself)
#
# simplifying classification
#  - Real/Fake classification decision
#  - 1 - 10 confidence in that decision.
# or
#  - Real/Fake (or Valid/Invalid) classification
#  - Single range number, 0 (or .1 or 1) being full confidence in fake, 1 (or 10) being full confidence in real. So .49 being little confidence fake and .51 being little confidence real.
#
# true/falase
# howconfidence? 0idk, 1really
#
# true/false
# range true/false .5 idk, .49falsedk, 0realfalse, 51trueidk, 1realtrue
#
#
# The holistic classifications (pan?) and per component evaluations are not mutually exclusive. They can be applied to both (as we've done so far).
# Reconsiling Pan's broader (and somewhat human interpretation influenced) categories with the precise values is a thing to think about.

# something with WEIGHTS ? of components? down the line... ?
# science journal doesn't put titles.
# title high weight, journal high, page lower, pmid lower... ? what uses? weight in what equations?
# older articles (2000s, 1990s, etc.) will have no DOIs. @todo regen dataset with bigger DATE RANGE and more random ordering (not just pub order. for variety). 
# as tangent, date range is a thing to think about in our methodology, the testing we're doing. for the paper. influence of corresponding years with llms?

# chatbots holistic evaluation 
# will also have per component evaluation INSIDE
# interesting to see how it matches up?
# But chatbot holistic is not our deterministic combination of it's component evaluations. It is it's own decision.
#  Though we could do that as well, and compare. Again same as seeing how the two line up.
#  Of course we'll know the corret answers too. Exactly what's been done on each reference, which components it comprises.
#  Could we in addition, also do some manual weighted score based on the ground-truth modifications we know exist in the reference? Compare that with model holistic, and our averaging of model component scores?

# Putting refs into something more specific like pans categories could be a seperate problem. 
# A more difficult one, since we're defining more things.
# Placing category cutoffs along some range 0 -> 1? .8 suspect, 1 real, .2 badbad... ?

# ryan implemented internet search locally, which works. Second pass adhers to json schema.
# jackson is working on csv files
# gabriel did the stuff with reference baking, format component codes. Now onto absent component mutations.

# Create a set entry from reference data
def ds_entry(rd, *, ID=None):
    return { "id": ID,                  # Internal ID + original PMCID
             "src_id": rd["pmcid"],
             #"modcode": 0b00000000,     # Signals mutated components + degree of mutation. 
             #"modflags": [],
             "mutcode": 0b00000000,     # Describes specific mutations.
             "mutflags": [],
             "compconfs": {},           # Component : "suggested confidence score". Key existence signal component modification as well.
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
        #entry["format"] = RB.bake_formats(entry["data"])
        entry["format"] = F.compile_all(entry["data"])
        entry["mutlabels"] = EntryMutator.explain_mutcode(entry["mutcode"])


# Class of methods to mutate dataset entries using ref_mutator functions.
class EntryMutator:
    # There are components, and there are mutations.
    # One type of mutation can work on multiple component types. Other types only a few.

    # THE MATTER OF GRADING REFERENCE MUTATION SEVERITY / MODEL DETECTION PERFORMANCE
    # Different mutation types have different levels of "validity" (in the sense of the reference being human-made vs generated).
    # Mutation validity is stored similar way to model's classification confidences, 0 (>conf invalid) -> .49 (<conf) -> .5 (ambig) -> .51 (<conf) 1 (>conf valid).
    # This (along with grading valid / invalid classification in a binary way) is a a method of grading chatbot fake reference detection performance

    # Mutations: typo, mismatch, hallucinate, shuffle,
    # COMPONENT_LIST = ("authors", "title", "journal_name", "journal_volume", "journal_issue", "journal_page",
    #                   "elocator", "publication_date", "doi", "url_abstract", "url_direct", "pmcid", "pmid")

    # Define which mutations are valid per component, and the degrees of invalidity.
    _MUTMAP = {
        "authors":          [("typo", .50), ("mismatch", .00),  ("hallucinate", .00),   ("shuffle", .25)],          # @ this is kind of like the 'weight' stuff with scoring, but applied to how much (thing being wrong) tarnishes the "validity" of a reference.
        "title":            [("typo", .50), ("mismatch", .00),  ("hallucinate", .00)],
        "journal_name":     [("typo", .50), ("mismatch", .00),  ("hallucinate", .00)],
        "journal_volume":   [                                   ("hallucinate", .00)],
        "journal_issue":    [                                   ("hallucinate", .00)],
        "journal_page":     [                                   ("hallucinate", .00)],                  # @todo we REALLY need to add the 'missing component' thing. Maybe. That would give reason for more variety in the weighting (not just .5 typos and 0 all else)
        "elocator":         [               ("mismatch", .00),  ("hallucinate", .00)],
        "publication_date": [                                   ("hallucinate", .00)],                  # @ consider, when would it be above .5? Never really, cause we know it's been modified. Above .5 would incentivize confidence in the wrong answer... Right?
        "pmcid":            [("typo", .50), ("mismatch", .50),  ("hallucinate", .00)],                  # How are we going to compare their scores against this? Will it just be closeness, or does the funny business around the .5 interfere with that?
        "pmid":             [("typo", .50), ("mismatch", .50),  ("hallucinate", .00)],
        "doi":              [("typo", .50), ("mismatch_prefix", .00),   ("hallucinate_prefix", .50),
                                            ("mismatch_suffix", .00),   ("hallucinate_suffix", .50)]    # ! @todo Inconsistency with DOI prefix and suffix thing.
        #"url_abstract":     ("typo", "mismatch", "hallucinate"),
        #"url_direct":       ("typo", "mismatch", "hallucinate"),
    }
    # Map assigned "correct" confidence values to each mutation.                                @ EMAIL DON is this even the right way to go about grading them ????? idk.......... can't think..... of anything ... better..
    _MUTCONFS = {comp: {mutconf[0]: mutconf[1] for mutconf in mutconfs} for comp, mutconfs in _MUTMAP.items()}
    # Map unique bits to each mutation.
    _MUTFLAGS = {}
    _MUTLABELS = {} # Bake some human readable labels for convenience.
    bit = 1
    for comp, muts in _MUTMAP.items():              # @note: the best and most flexible thing to do would be assign a set # of bits per component, each bit position relative to each block start represents the same mutation type. But, WHO CARES!
        _MUTFLAGS[comp] = {}
        for mut in muts:
            _MUTFLAGS[comp][mut[0]] = bit
            _MUTLABELS[bit] = f"{comp}::{mut}"
            bit = bit << 1
    del bit
    print(*[str(i)+"\n" for i in _MUTFLAGS.items()])
    for bit in _MUTLABELS: print(_MUTLABELS[bit])
    # Some human readable flat labels.
    #_MUTLABELS = [f"{comp}_{mut}[{muts[mut]}]" for comp, muts in _MUTFLAGS.items() for mut in muts]

    # Create flat unique labels for all possible mutations.
    #_MUTLABELS = [f"{comp}_{mut}" for comp, muts in _MUTMAP.items() for mut in muts]
    # Assign bit to each mutation.
    #_MUTFLAGS = {flag: 2**i for i, flag in enumerate(_MUTLABELS)}
    #_MUTFLAGS = {comp: {mut: i1+(2**i2 for mut in _MUTMAP(comp)} for comp, i, 

    # Keeping for temporary (lmao) translation
    _MUTFLAGS_DEPRECATED = ("author_typo",          "author_mismatch",  "author_hallucinate",   "author_shuffle",   # Note: not all mutations are combinable (overwrites).
                 "title_typo",           "title_mismatch",   "title_hallucinate",                        # Also, be wary in the setting of these flags. A wrongly set flag will not reveal itself.
                 "jname_typo",           "jname_mismatch",   "jname_hallucinate",
                 "jvol_hallucinate",     "jiss_hallucinate", "jpage_hallucinate",
                 "elocator_mismatch",    "elocator_hallucinate",
                 "pubs_hallucinate",    #"epub_randomize")
                 "doi_typo", "doi_mismatch_prefix", "doi_mismatch_suffix", "doi_hallucinate_prefix", "doi_hallucinate_suffix",
                 "pmid_typo", "pmid_mismatch", "pmid_hallucinate", "pmcid_typo", "pmcid_mismatch", "pmcid_hallucinate")
    #print(*[a+" "+b+"\n" for a, b in zip(_MUTLABELS,_MUTFLAGS_DEPRECATED)])


    # Mutation flags. Describe exactly which modifications were performed on a reference dataset entry.
    #_MUTFLAGS_MAP =     _MUTFLAGS_FLAT = 
#    # Modification flags. Signals which general components have had a modification applied. Is just a list of the modified components. 
#    _MODFLAGS = COMPONENT_LIST.copy()
#    # *note: There is a more clever (less stupid) way to do this. But who cares, it probably won't be a problem.
#    for f in _MUTFLAGS:
#        if "author" in f: _MODFLAGS[f] = "authors"
#        elif "title" in f: _MODFLAGS[f] = "title"
#        elif "jname" in f: _MODFLAGS[f] = "journal_name"
#        elif "jvol" in f: _MODFLAGS[f] = "journal_volume"
#        elif "jiss" in f: _MODFLAGS[f] = "journal_issue"
#        elif "jpage" in f: _MODFLAGS[f] = "journal_page"
#        elif "elocator" in f: _MODFLAGS[f] = "elocator"
#        elif "pubs" in f: _MODFLAGS[f] = "publication_date"
#        elif "doi" in f: _MODFLAGS[f] = "doi"
#        #elif "url_abstract":
#        #elif "url_direct":
#        elif "pmcid" in f: _MODFLAGS[f] = "pmcid"
#        elif "pmid" in f: _MODFLAGS[f] = "pmid"
#        else: print("!!!! BADBADBAD !!!!")

    def __init__(self, *, component_set, h_titles, h_authors, h_journals, rand_year_range):
        # Resources for hallucination and mismatch mutations
        self._COMPONENTS = component_set            # Alternatively, if we think a hallucination sample for every component is a good idea:
        self._FAKE_TITLES = h_titles                # self._REAL_COMPONENTS
        self._FAKE_AUTHORS = h_authors              # self._FAKE_COMPONENTS
        self._FAKE_JOURNALS = h_journals            # The issue is, how fake can a date, DOI, or PMCID get? Fake enough to warrant that?
        self._RAND_YEAR_RANGE = (rand_year_range[0], rand_year_range[1])
### little helpers

    # Return list of mutation labels from mutcode.
#    @classmethod
#    def explain_mutcode_deprecated(cls, code):
#        return [label for label in cls._MUTFLAG_BITS if (code & cls._MUTFLAG_BITS[label])]
    @classmethod
    def explain_mutcode(cls, code):
        #return [label for label in cls._MUTLABELS if (code & cls._MUTFLAG_BITS[label])]
        return cls._MUTLABELS[code] if code in cls._MUTLABELS else f"Bad Code: {code}"
    # Set mutation flag in ds_entry.
    @classmethod
    def _flag(cls, ds_entry, flag):
        ds_entry["mutcode"] = ds_entry["mutcode"] | cls._MUTFLAG_BITS[flag]       # @todo !!!! Some mutations undo other ones (like running a mismatch or hallucination after a type).
    def _flag(cls, ds_entry, c, m):
        # Set flag
        ds_entry["mutcode"] = ds_entry["mutcode"] | cls._MUTFLAGS[c][m]
        # Create or bring down conf score if 
        if c not in ds_entry["compconf"] or  cls._MUTCONFS[c][m] < ds_entry["compconf"][c]:
            ds_entry["compconf"][c] = cls._MUTCONFS[c][m]
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
        ds_entry["data"]["journal"]["name"] = self._randcopy([jname for jname in self._COMPONENTS["sets"]["journal_name"] if jname != ds_entry["data"]["journal"]["name"]])
        self._flag(ds_entry, "jname_mismatch")
        return ds_entry
    def jname_hallucinate(self, ds_entry):
        ds_entry["data"]["journal"]["name"] = self._randcopy(self._FAKE_JOURNALS)    # @todo: !! Make sure the fake_journal source contains both full and short names, and that the file is parsed into the proper dict format!
        self._flag(ds_entry, "jname_hallucinate")
        return ds_entry

### JOURNAL VOLUME / ISSUE

    def jvol_hallucinate(self, ds_entry):             # @todo: Consider: Should we bother doing mismatches / hallucinations for the numerics?
        if (vol := ds_entry["data"]["journal"]["volume"]):  # Not all references contain vol/iss data.
            vol = int(vol)
            ds_entry["data"]["journal"]["volume"] = random.choice([v for v in range(int(vol*.5), int(vol*1.5)) if v != vol]) # Arbitrary. Randomization range is the volume +/- half
        else:
            ds_entry["data"]["journal"]["volume"] = random.randint(0,500)
            print(f" ! empty vol in {ds_entry["id"]} {ds_entry["src_id"]}, setting to niave random: {ds_entry["data"]["journal"]["volume"]}")
        self._flag(ds_entry, "jvol_hallucinate")
        return ds_entry

    def jiss_hallucinate(self, ds_entry):
        if (iss := ds_entry["data"]["journal"]["issue"]):
            iss = int(iss)
            ds_entry["data"]["journal"]["issue"] = random.choice([i for i in range(int(iss*.5), int(iss*1.5)) if i != iss])
        else:
            # @todo: If we want to ensure that we create a database subset with vols and iss randomizations, we could return a None to signal.
            #        ALTERNATIVE would be to fail around it, and put some random number anyways.
            #ds_entry["data"]["journal"]["issue"] = random.choice(self._COMPONENTS["journal"])["issue"] # !! It must be that the same empties exist in the compset. SO, just do a random number.
            ds_entry["data"]["journal"]["issue"] = random.randint(0,1500)
            print(f" ! empty iss in {ds_entry["id"]} {ds_entry["src_id"]}, setting to niave random: {ds_entry["data"]["journal"]["issue"]}")
        self._flag(ds_entry, "jiss_hallucinate")
        return ds_entry

    # Could also perchance do a jissvol_mismatch (if one of our classifications implies it)

### JOURNAL PAGE NUMBERS

    def jpage_hallucinate(self, ds_entry):
        spage = random.randint(23, 1184)    # Completely arbitrary randomness.
        length = random.randint(3, 51)
        ds_entry["data"]["journal"]["page"]["start"] = spage
        ds_entry["data"]["journal"]["page"]["end"] = spage+length
        self._flag(ds_entry, "jpage_hallucinate")
        return ds_entry

    # Other possibilities: mismatch, nonesense_randomize (end < start)
    # If we do mismatches for these ones, that would make a big jALL_mismatch easy. Though it would be regardless, cause of compset structure. Whatever.

    # @todo still
    # elocator mismatch, randomize, typo? For typo, what about off by one and swaps?
    # URL typo, mismatch, randomize?
    def elocator_mismatch(self, ds_entry):  # @Consider: What about when an article doesn't have an elocator (or any other thing), should the mismatch still occur?
        ds_entry["data"]["journal"]["elocator"] = self._randcopy([eloc for eloc in self._COMPONENTS["sets"]["journal_elocator"] if eloc != ds_entry["data"]["journal"]["elocator"]])
        self._flag(ds_entry, "elocator_mismatch")
        return ds_entry

    def elocator_hallucinate(self, ds_entry):
        num = str(random.randint(1, 999999))
        ds_entry["data"]["journal"]["elocator"] = "e"+"0"*(6-len(num))+num
        self._flag(ds_entry, "elocator_hallucinate")
        return ds_entry

### JOURNAL / DIGITAL PUBLICATION DATES

    #def pub_mismatch(self, ds_entry):
    #def epub_mismatch(self, ds_entry): pass

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
            self._flag(ds_entry, "pubs_hallucinate")
        return ds_entry
#    def epub_randomize(self, ds_entry, *, y=True, m=True, d=True):
#        if y: ds_entry["data"]["epub"]["y"] = random.randint(*self._RAND_YEAR_RANGE)
#        if m: ds_entry["data"]["epub"]["m"] = random.randint(1, 12)
#        if d: ds_entry["data"]["epub"]["d"] = random.randint(1, 31)
#        if y or m or d: self._flag(ds_entry, "epub_randomize")
#        return ds_entry

### DOI

    def doi_typo(self, ds_entry):                       # @todo: Consider: If we do typo's on numerics, should they include fatfinger or only swap? The assumption is that fatfinger typos are too rare in this case (letters in a number would be seen and fixed).
        doi = ds_entry["data"]["doi"]
        doi["prefix"] = T.typo_swapletter(doi["prefix"], random.choice([i for i, char in enumerate(doi["prefix"]) if char != "0"])) # Swap one char in the prefix (not zeros).
        doi["suffix"] = T.typofy(doi["suffix"]) # Just run the standard typo procedure on the suffix.
        self._flag(ds_entry, "doi_typo")
        return ds_entry

    def doi_mismatch_prefix(self, ds_entry):
        ds_entry["data"]["doi"]["prefix"] = self._randcopy([p for p in self._COMPONENTS["sets"]["doi_prefix"] if p != ds_entry["data"]["doi"]["prefix"]])
        self._flag(ds_entry, "doi_mismatch_prefix")
        return ds_entry

    def doi_mismatch_suffix(self, ds_entry):
        ds_entry["data"]["doi"]["suffix"] = self._randcopy([s for s in self._COMPONENTS["sets"]["doi_suffix"] if s != ds_entry["data"]["doi"]["suffix"]])
        self._flag(ds_entry, "doi_mismatch_suffix")
        return ds_entry

    def doi_hallucinate_prefix(self, ds_entry):
        # 10.random1000->9999 + .random0->10or100or1000 (0-2x)
        ds_entry["data"]["doi"]["prefix"] = ".".join(["10", str(random.randint(1000, 9999))] + [str(random.randint(0, 10**random.randint(1, 3))) for i in range(random.randint(0,2))])
        self._flag(ds_entry, "doi_hallucinate_prefix")
        return ds_entry

    def doi_hallucinate_suffix(self, ds_entry):
        # 1-3 groups of 3 to 8 random numbers and letters
        ds_entry["data"]["doi"]["suffix"] = "-".join(["".join([random.choice("abcdefghijklmnopqrstuvwxyz,./12345678900987654321") for i in range(random.randint(3, 8))]) for i in range(random.randint(1, 3))])
        self._flag(ds_entry, "doi_hallucinate_suffix")
        return ds_entry

### URLS

    # ...       @todo something with the URLs???

### PMIDS / PMCIDS

    def pmid_typo(self, ds_entry):
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
        self._flag(ds_entry, "pmid_typo")
        return ds_entry

    def pmid_mismatch(self, ds_entry):
        ds_entry["data"]["pmid"] = self._randcopy([ID for ID in self._COMPONENTS["pmid"] if ID != ds_entry["data"]["pmid"]])
        self._flag(ds_entry, "pmid_mismatch")
        return ds_entry

    def pmid_hallucinate(self, ds_entry):
        ds_entry["data"]["pmid"] = str(random.randint(1, 999999999)) # Up to 9 digits.
        self._flag(ds_entry, "pmid_hallucinate")
        return ds_entry

    # Basically all exact same.
    def pmcid_typo(self, ds_entry):
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
        self._flag(ds_entry, "pmcid_typo")
        return ds_entry

    def pmcid_mismatch(self, ds_entry):
        ds_entry["data"]["pmcid"] = self._randcopy([ID for ID in self._COMPONENTS["pmcid"] if ID != ds_entry["data"]["pmcid"]])
        self._flag(ds_entry, "pmcid_mismatch")
        return ds_entry

    def pmcid_hallucinate(self, ds_entry):
        ds_entry["data"]["pmcid"] = "PMC"+str(random.randint(1, 99999999)) # Up to 8 digits. Plus PMC prefix.
        self._flag(ds_entry, "pmcid_hallucinate")
        return ds_entry


# @todo: Consider: Should we just blanket each element with the same boilerplate mutation methods, even when it might not make complete sense? (such as mismatches on vol/iss, or hallucinating page numbers?)


# @todo: Consider: What about mutations which work on the final format itself? Like swaping a full journal name with an abreviation or vice versa? 
#                  Is such an error to minute to test, will it make a difference?
#                  We could just set the flag. Then it would be the format baker's responsibility to read it and bake accordingly.




    # Mutation level. Or, the classification of a reference based on the sum of it's mutations.
    # Differentiates between ambigious "human-esque" reference mistakes, and undeniably "chatbot-esque" hallucinations.
