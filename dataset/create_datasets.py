
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
    with open(f"{DIR}/h_authors.txt", "r") as f: h_author_src = [line.strip() for line in f if line.strip()]
    with open(f"{DIR}/h_journals.txt", "r") as f: h_journal_src = [line.strip() for line in f if line.strip()]

    # Make datasets from source references.
    # * going by the five preliminary subsets outlined by Dr Pan, @todo: refine definitions.
    datasets = { "source":        make_dataset(refdata_src),
                 "minor_mderror": make_dataset(refdata_src),
                 "major_mderror": make_dataset(refdata_src),   # Could also do splits here (refdata[0:25])
                 "plausible_fab": make_dataset(refdata_src),
                 "human_review":  make_dataset(refdata_src) }

    # Configure the sets (mutate reference data) accordingly.
    setconfig.init(h_titles=h_title_src, h_authors=h_author_src, h_journals=h_journal_src, component_set=compset_src)

    #setconfig.minor_mderror(datasets["minor_mderror"])
    #setconfig.major_mderror(datasets["minor_mderror"])

    # Bake formatted references from (now modified) references data.
    for ds in datasets: bake_dataset(datasets[ds])

    print(json.dumps(datasets, indent=2))
