
import datasets as DS
import json

# Builds datasets from a source reference file.
# Uses ref_mutators to create bad references/datasets.
# Again, no error handling in any of this. Will break if it breaks.

# Creating datasets from reference_data.json, mutating references with EntryMutator.
if __name__ == "__main__":
    ref_data = None
    with open("./data2/reference_data.json", "r") as f: ref_data = json.load(f)

    # Create sets of ds_entries for source references, hallucinated title references, and mismatched title references. @todo: more
    source_ds = DS.create_dataset(ref_data, v=True)
    title_hallucinate_ds = DS.create_dataset(ref_data[0:25], v=True)
    title_mismatch_ds = DS.create_dataset(ref_data[25:50], v=True)

    # Creating DS entry mutator
    cs, ft = None, None
    with open("./data2/component_set.json", "r") as f:
        cs = json.load(f)
    with open("./data/fake_titles.txt", "r") as f:
        ft = [line.strip() for line in f if line.strip()]
    M = DS.EntryMutator(component_set = cs, fake_titles = ft, fake_authors = [], fake_journals = [])

    # Applying mutations to references (entries in dataset) 
    for entry in title_hallucinate_ds:
        M.title_hallucinate(entry)
    for entry in title_mismatch_ds:
        M.title_mismatch(entry)

    # Combining datasets and baking reference formats.
    complete_ds = source_ds + title_hallucinate_ds + title_mismatch_ds
    DS.bake_formats(complete_ds)

    print(json.dumps(complete_ds[125:], indent=2))
