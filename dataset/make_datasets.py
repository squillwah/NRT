
import datasets as DS
import random
import json

# Builds datasets from a source reference file.
# Uses ref_mutators to create bad references/datasets.
# Again, no error handling in any of this. Will break if it breaks.

# Creating datasets from reference_data.json, mutating references with EntryMutator.
if __name__ == "__main__":
    ref_data = None
    with open("./reference_data.json", "r") as f: ref_data = json.load(f)

    # Create sets of ds_entries for source references, hallucinated title references, and mismatched title references. @todo: more
    source_ds = DS.create_dataset(ref_data, v=True)
    title_hallucinate_ds = DS.create_dataset(ref_data[0:25], v=True)
    title_mismatch_ds = DS.create_dataset(ref_data[25:50], v=True)

    # Applying title mutations.
    M = DS.EntryMutator(title_f="./data/fake_titles.txt", component_f="./data/component_set.json")
    for entry in title_hallucinate_ds:
        M.title_hallucinate(entry)
    for entry in title_mismatch_ds:
        M.title_mismatch(entry)

    # Combining datasets and baking reference formats.
    complete_ds = source_ds + title_hallucinate_ds + title_mismatch_ds
    DS.bake_formats(complete_ds)

    print(json.dumps(complete_ds, indent=2))
