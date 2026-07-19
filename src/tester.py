#import tools.datasets.curves
from tools.datasets.mutators import EntryMutator, MutationType
import tools.datasets.dataset as ds
import json
import tools.help as h

if __name__ == "__main__":
    # Open source files 
    HDIR = "./data/source_hallucinations"
    DIR = "./data/source_references1"
    refdata_src = None
    compset_src = None
    h_title_src = None
    h_author_src = None
    h_journal_src = None

    with open(f"{DIR}/refdata.json", "r") as f: refdata_src = json.load(f)
    with open(f"{DIR}/compset.json", "r") as f: compset_src = json.load(f)
    with open(f"{HDIR}/h_titles.txt", "r") as f: h_title_src = [line.strip() for line in f if line.strip()]
    with open(f"{HDIR}/h_authors.json", "r") as f: h_author_src = json.load(f)
#        h_author_src = [{"l": "FAKEAUTH", "f": "FAKEAUTH"}]*200 #{ "l": name, "f": name for name in [line.strip() for line in f if line.strip()]} # Placeholder. Either parse by ', ' or have source generate a json of last and first.
    with open(f"{HDIR}/h_journals.json", "r") as f: h_journal_src = json.load(f)
#        h_journal_src = [{"full": "FAKEJOURN", "short": "FAKEJOURN"}]*200 #{ "full": name, "short": name for name in [line.strip() for line in f if line.strip()]} # Placeholder. Have the source be a JSON with {full, short}

#    print(json.dumps(h_author_src, indent=2))    
#    print(json.dumps(h_journal_src, indent=2))    
#    print(h_title_src)    
#    quit()
    refdata_src = [refdata_src[0]]
    one = ds.make_dataset(refdata_src) # Source references, with four duplicates. (100 + 400 = 500)
    print(json.dumps(one, indent=2)) 

    M = MutationType
    EM = EntryMutator(h_titles=h_title_src, h_authors=h_author_src, h_journals=h_journal_src, component_set=compset_src, rand_year_range=(2005, 2021))
    
    print(EM.mutations())

    # Testing all omissions
    omittables = [(comp, mut) for comp, muts in EM.mutations().items() for mut in muts if mut == M.OMISSION]
    print(json.dumps(omittables, indent=2))

    for comp, mut in omittables:
        EM.mutate(one[0], comp, mut)

    ds.bake_dataset(one)
    
    print(json.dumps(one, indent=2))
