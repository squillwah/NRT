
from dstools.datasets import make_dataset, bake_dataset
import dstools.configurations as setconfig
import json

# This is the thing.

# Make datasets from reference data.
# Mutate references with dataset configuration procedures.

if __name__ == "__main__":
    # Open source files 
    DIR = "./reference_source"
    refdata_src = None
    compset_src = None
    h_title_src = None
    h_author_src = None
    h_journal_src = None

    with open(f"{DIR}/refdata.json", "r") as f: refdata_src = json.load(f)
    with open(f"{DIR}/compset.json", "r") as f: compset_src = json.load(f)
    with open(f"{DIR}/h_titles.txt", "r") as f: h_title_src = [line.strip() for line in f if line.strip()]
    with open(f"{DIR}/h_authors.txt", "r") as f:
        h_author_src = [{"l": "FAKEAUTH", "f": "FAKEAUTH"}]*200 #{ "l": name, "f": name for name in [line.strip() for line in f if line.strip()]} # Placeholder. Either parse by ', ' or have source generate a json of last and first.
    with open(f"{DIR}/h_journals.txt", "r") as f:
        h_journal_src = [{"full": "FAKEJOURN", "short": "FAKEJOURN"}]*200 #{ "full": name, "short": name for name in [line.strip() for line in f if line.strip()]} # Placeholder. Have the source be a JSON with {full, short}

    # Make datasets from source references.
    # * going by the five preliminary subsets outlined by Dr Pan, @todo: refine definitions.
    datasets = { "source":        make_dataset(refdata_src),
                 "minor_mderror": make_dataset(refdata_src),
                 "major_mderror": make_dataset(refdata_src),   # Could also do splits here (refdata[0:25])
                 "plausible_fab": make_dataset(refdata_src),
                 "human_review":  make_dataset(refdata_src) }

    # Configure the sets (mutate reference data) accordingly.
    setconfig.init(h_titles=h_title_src, h_authors=h_author_src, h_journals=h_journal_src, component_set=compset_src)

    #setconfig.apply_minor_mderror(datasets["minor_mderror"])
    #setconfig.apply_major_mderror(datasets["minor_mderror"])

    # Bake formatted references from (now modified) references data.
    for ds in datasets: bake_dataset(datasets[ds])

    #print(json.dumps(datasets, indent=2))

#    # Testing typo shit
#    testsubset = datasets["source"][0:2]
#    #testsubset[0]["data"]["authors"][0]["l"] = ""
#    orig = []
#    typo = []
#    for entry in testsubset:
#        orig.append([name['l']+", "+name['f'] for name in entry["data"]["authors"]])
#    setconfig.test(testsubset)
#    for entry in testsubset:
#        typo.append([name['l']+", "+name['f'] for name in entry["data"]["authors"]])
#
#    for olist, tlist in zip(orig, typo):
#        for o, t in zip(olist, tlist):
#            print(o)
#            print(t)
#            print("-"*20)
#
#    #print("\n".join([name['l']+", "+name['f'] for name in entry["data"]["authors"]]))
#
#    #print(json.dumps(testsubset, indent=2))


    # ! Consider: Is there such a thing as authors with only first or only last names? How are those layed out in RIS, and will that cause errors (subtle, undetectable)?



    # Testing tests ...  
    dataset = datasets["source"]
#    print("===MISMATCHTEST===")
#    setconfig.test_mismatch(dataset)
#    bake_dataset(dataset)
#    print(json.dumps(dataset, indent=2))
#
#    print("===TYPOTEST===")
#    setconfig.test_typos(dataset)
#    bake_dataset(dataset)
#    print(json.dumps(dataset, indent=2))
#
#    print("===HALLUCINATETEST===")
#    setconfig.test_hallucinate(dataset)
#    bake_dataset(dataset)
#    print(json.dumps(dataset, indent=2))

    setconfig.test_voliss(dataset)
    bake_dataset(dataset)
    print(json.dumps(dataset, indent=2))
