
from pathlib import Path

from tools.datasets.dataset import make_dataset, bake_dataset
from tools.datasets.probabilities import MutationProbability
from tools.datasets.mutators import EntryMutator
from tools.datasets.curves import MutationCurves
from tools.datasets.mutators import MutationType as M
from tools.references.refdata import ReferenceComponent as C

import tools.help as h
import random
import json


# Generating a mutated reference set from source reference data.

MUTATED_SOURCE_RATIO = 1   # Fill the set with ten mutated references from every source.

DIR_OUTPUT = Path("./data/")
DIR_REFERENCES = Path("./data/source/references1")
DIR_EXTRA = Path("./data/source/extra/")

refs = h.read_json(DIR_REFERENCES / "refdata.json")

EM = EntryMutator(
        compset     = h.read_json(DIR_REFERENCES / "compset.json"),
        htitles     = h.read_json(DIR_EXTRA / "h_titles.json"),
        hauthors    = h.read_json(DIR_EXTRA / "h_authors.json"),
        hjournals   = h.read_json(DIR_EXTRA / "h_journals.json"),
        hyear_range = (2000, 2021)
    )

MP = MutationProbability(
        subset_size = len(refs)*MUTATED_SOURCE_RATIO,
        curves      = MutationCurves
    )

dataset = make_dataset(refs, MUTATED_SOURCE_RATIO)  # Initializing dataset of refs + 10*refs.

# @TODO Precedence and conflict mutation checks, either here or in EntryMutator.mutate()
# Entries are all assigned IDs. First 0 -> len(refs) are source references (not to mutate).

# For each entry in the mutated subset, chance each mutation using their probabilties along the set gradient.

mutations = EM.mutations(flat=True) # (Component, Mutation) tuples, complete list of all possible
# Reorder mutations so omissions are checked first.
# Once an omission is applied, nothing else can be ... ?

# OR OR OR !
# Probably best thing is to just put checking and FIXING in mutate()
#  So if an omission is applied and then another thing, the other thing gets removed.
#  and vice versa.
#  Should be easy to do with the mapping my component, can just check if mut == omission, undo all mutation[comp] (and hard reset the severity score to omission). might want a different func than _flag



for x, ID in enumerate(range(len(refs), len(dataset))):
    random.shuffle(mutations)   # Shuffle to avoid bias from sequence (mutations can negate others)
    h.log(ID, dataset[ID]["id_source"]) 
    for component, mutation in mutations:
        p = MP.probability(component, mutation, x)
        if random.random() < p:
            # Apply it.
            EM.mutate(dataset, ID, component, mutation)

# Render citation format styles, score component severities... other stuff probably.
bake_dataset(dataset)

h.write_json(dataset, DIR_OUTPUT / "set.json")

# Can we track actual distribution, and make another graph to compare with probability?
