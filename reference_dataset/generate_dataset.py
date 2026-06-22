
from source_refs import get_papers_filter, get_ris#extract_reference_formats
from parse_refs import parse_ris, component_set
from copy import deepcopy
import ref_mutators as RM
import ref_builders as RB
import json

# Again, no error handling in any of this. Will break if it breaks.

JOURNALS = {"BMJ": 25,
            "Nature": 25,
            "Lancet": 25,
            "NEJM": 25}

def ds_entry(rd):
    return { "id": rd["pmcid"],        # Should we use PMID, PMCID, or some internal thing (just in index?).
             "errors": 0b00000000,
             "data": deepcopy(rd),
             "format": {} }

# 1 Search for article IDs

pmcids = []
for j in JOURNALS:
    #print(f"Fetching {JOURNALS[j]} articles from {j}...")
    pmcids.extend(get_papers_filter(JOURNALS[j], f"{j}[Journal]"))  # Grabs most recent. Can add sort functionality later depending on goals.

#print(json.dumps(pmcids, indent=2))
#print(len(pmcids))

# 2 Get RIS data and formalize

raw_ris = get_ris(*pmcids)
ref_data = [parse_ris(ris) for ris in raw_ris]

# 3 Create dataset and internal component set

dataset = [ds_entry(ref) for ref in ref_data]
#componentset = component_set(ref_data)

# 4 Mutate refs and add to data set

# ... placeholder ...
mutated_dataset = []
for ref in ref_data:
    mref = ds_entry(ref)

    # do mutations ...
    # badify_auths(mref) # Will | error code accordingly

    mutated_dataset.append(mref)
    break

dataset.extend(mutated_dataset)

# Bake reference formats
for ref in dataset:
    for f in RB.FORMATS:
        ref["format"][f] = RB.build_ref(ref["data"], f)
    break

print(json.dumps(dataset[0], indent=2))





