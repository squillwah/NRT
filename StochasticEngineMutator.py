import json
import random
from copy import deepcopy
from enum import StrEnum

# start off with pasting one of ravi's "puzzle pieces". a defined component that focuses on listing and grouping the
# 'refdata2021under.json' data from the other file.
class ComponentType(StrEnum):
    AUTHORS = "authors"
    TITLE = "title"
    JOURNAL_NAME = "journal_name"
    JOURNAL_VOLUME = "journal_volume"
    JOURNAL_ISSUE = "journal_issue"
    JOURNAL_PAGE = "journal_page"
    ELOCATOR = "elocator"
    PUBLICATION_DATE = "publication_date"
    DOI = "doi"
    URL_ABSTRACT = "url_abstract"
    URL_DIRECT = "url_direct"
    PMCID = "pmcid"
    PMID = "pmid"

# defines the different mutation types that can appear, which is a callback to dataset.py.
class Mutation(StrEnum):
    TYPO = "typo"
    MISMATCH = "mismatch"
    HALLUCINATION = "hallucination"
    SHUFFLE = "shuffle"
    OMISSION = "omission"

# aliases that basically match what ravi programmed.
C = ComponentType
M = Mutation

# the mutation map, which matches the kind of errors we can get to their respective components.
# it has the "(component, mutation)" style to it, which moves everything to EntryMutator
MUTATION_DISPATCH = {
    (C.AUTHORS, M.TYPO): "author_typo",
    (C.AUTHORS, M.SHUFFLE): "author_shuffle",
    (C.AUTHORS, M.MISMATCH): "author_mismatch",
    (C.AUTHORS, M.HALLUCINATION): "author_hallucinate",
    (C.AUTHORS, M.OMISSION): "drop_authors",

    (C.TITLE, M.TYPO): "title_typo",
    (C.TITLE, M.MISMATCH): "title_mismatch",
    (C.TITLE, M.HALLUCINATION): "title_hallucinate",
    (C.TITLE, M.OMISSION): "drop_title",

    (C.JOURNAL_NAME, M.TYPO): "jname_typo",
    (C.JOURNAL_NAME, M.MISMATCH): "jname_mismatch",
    (C.JOURNAL_NAME, M.HALLUCINATION): "jname_hallucinate",
    (C.JOURNAL_NAME, M.OMISSION): "drop_journal_name",

    (C.JOURNAL_VOLUME, M.HALLUCINATION): "jvol_hallucinate",
    (C.JOURNAL_VOLUME, M.OMISSION): "drop_volume",

    (C.JOURNAL_ISSUE, M.HALLUCINATION): "jiss_hallucinate",
    (C.JOURNAL_ISSUE, M.OMISSION): "drop_issue",

    (C.JOURNAL_PAGE, M.HALLUCINATION): "jpage_hallucinate",
    (C.JOURNAL_PAGE, M.OMISSION): "drop_pages",

    (C.ELOCATOR, M.MISMATCH): "elocator_mismatch",
    (C.ELOCATOR, M.HALLUCINATION): "elocator_hallucinate",
    (C.ELOCATOR, M.OMISSION): "drop_elocator",

    (C.PUBLICATION_DATE, M.HALLUCINATION): "pubs_hallucinate",
    (C.PUBLICATION_DATE, M.OMISSION): "drop_publication_date",

    (C.DOI, M.TYPO): "doi_typo",
    (C.DOI, M.MISMATCH): "doi_mismatch_suffix",
    (C.DOI, M.HALLUCINATION): "doi_hallucinate_suffix",
    (C.DOI, M.OMISSION): "drop_doi",

    (C.PMID, M.TYPO): "pmid_typo",
    (C.PMID, M.MISMATCH): "pmid_mismatch",
    (C.PMID, M.HALLUCINATION): "pmid_hallucinate",

    (C.PMCID, M.TYPO): "pmcid_typo",
    (C.PMCID, M.MISMATCH): "pmcid_mismatch",
    (C.PMCID, M.HALLUCINATION): "pmcid_hallucinate",
}

# defining here what kinds of mutations are allowed. per each tier. this is what ryan was defining in terms of
# needing human review, etc.
SEVERITY_POLICIES = {
    # no errors
    "tier_0": {
        "budget_range": (0, 0),
        "allowed_mutations": []
    },
    # typos, formatting errors
    "tier_1": {
        "budget_range": (1, 2),
        "allowed_mutations": [M.TYPO, M.SHUFFLE]
    },
    # metadata drift, scrapers, mismatched components. middle of the road
    "tier_2": {
        "budget_range": (2, 3),
        "allowed_mutations": [M.TYPO, M.SHUFFLE, M.MISMATCH, M.OMISSION]
    },
    # hallucinations, omissions
    "tier_3": {
        "budget_range": (3, 5),
        "allowed_mutations": [M.MISMATCH, M.HALLUCINATION, M.OMISSION]
    }
}


class StochasticEngine:
    def __init__(self, mutator_instance):
        self.mutator = mutator_instance

    def apply_stochastic_mutations(self, ds_entry, tier_label: str):
        policy = SEVERITY_POLICIES[tier_label]
        budget = random.randint(*policy["budget_range"])

        if budget == 0:
            return ds_entry

        applied_count = 0
        modified_components = set()
        candidates = []
        for (comp, mut) in MUTATION_DISPATCH.keys():
            if mut in policy["allowed_mutations"]:
                candidates.append((comp, mut))

        random.shuffle(candidates)

        for comp, mut in candidates:
            if applied_count >= budget:
                break

            # dont double mutate rule
            if comp in modified_components:
                continue

            # page vs elocator checker
            if comp == C.ELOCATOR and C.JOURNAL_PAGE in modified_components:
                continue
            if comp == C.JOURNAL_PAGE and C.ELOCATOR in modified_components:
                continue

            # entrymutator mapping thing
            method_name = MUTATION_DISPATCH.get((comp, mut))
            if not method_name:
                continue

            # 'gotcha b***h!' type of grabber of functions. then applies the mutations
            mutate_func = getattr(self.mutator, method_name, None)
            if mutate_func:
                try:
                    ds_entry = mutate_func(ds_entry)
                    modified_components.add(comp)
                    applied_count += 1
                except Exception as e:
                    # if key fails, then just push through it
                    continue

        return ds_entry



def build_gradient_dataset(raw_dataset, mutator_instance):
    engine = StochasticEngine(mutator_instance)
    total_records = len(raw_dataset)

    # appropriate division of the 100 IDs / citations
    tier_0_boundary = int(total_records * 0.20)
    tier_1_boundary = tier_0_boundary + int(total_records * 0.30)
    tier_2_boundary = tier_1_boundary + int(total_records * 0.30)
    mutated_dataset = []

    for idx, entry in enumerate(raw_dataset):
        entry_copy = deepcopy(entry)

        if idx < tier_0_boundary:
            tier = "tier_0"
        elif idx < tier_1_boundary:
            tier = "tier_1"
        elif idx < tier_2_boundary:
            tier = "tier_2"
        else:
            tier = "tier_3"

        processed_entry = engine.apply_stochastic_mutations(entry_copy, tier)
        processed_entry["severity_tier"] = tier
        mutated_dataset.append(processed_entry)

    return mutated_dataset


if __name__ == "__main__":
    # imports dataset.py
    try:
        from dataset import make_dataset, bake_dataset, EntryMutator
    except ImportError:
        pass

    # extract specific files
    INPUT_REFDATA = "UPDATED_reference_source/refdata2021under.json"  # Your pre-2022 articles
    OUTPUT_MUTATED = "UPDATED_reference_source/permuted_dataset.json"  # Final output file

    # had to do a bunch of extraction stuff to make my pycharm match up with the environment so there is this
    # with various folders and whatnot.
    DIR = "./reference_source"

    print(f"[*] Loading raw references from '{INPUT_REFDATA}'...")
    try:
        with open(INPUT_REFDATA, "r", encoding="utf-8") as f:
            raw_references = json.load(f)
    except FileNotFoundError:
        print(f"[!] Error: Could not find '{INPUT_REFDATA}'. Did you run download_references.py first?")
        exit(1)

    print("[*] Loading mutation resource sets...")
    try:
        with open(f"{DIR}/compset.json", "r") as f:
            compset_src = json.load(f)
        with open(f"{DIR}/h_titles.txt", "r") as f:
            h_title_src = [line.strip() for line in f if line.strip()]
        with open(f"{DIR}/h_authors.txt", "r") as f:
            h_author_src = [{"l": "FAKEAUTH", "f": "FAKEAUTH"}] * 200  # Placeholder fallback
        with open(f"{DIR}/h_journals.txt", "r") as f:
            h_journal_src = [{"full": "FAKEJOURN", "short": "FAKEJOURN"}] * 200  # Placeholder fallback
    except FileNotFoundError as e:
        print(f"[!] Warning: Some resource files were missing ({e}). Using mock fallbacks for mutation pools.")
        # mock pool so ravi's unloaded data doesn't crash the system / code
        compset_src = {"authors": [], "title": [], "pmid": [], "pmcid": [],
                       "sets": {"journal_name": [], "doi_prefix": [], "doi_suffix": [], "journal_elocator": []}}
        h_title_src = ["Fake Fabricated Title Studies"] * 100
        h_author_src = [{"l": "FakeLastName", "f": "FakeFirstName"}] * 100
        h_journal_src = [{"full": "Journal of Simulated Errors", "short": "J. Sim. Err."}] * 100


    print("[*] Initializing EntryMutator class...")
    mutator = EntryMutator(
        component_set=compset_src,
        h_titles=h_title_src,
        h_authors=h_author_src,
        h_journals=h_journal_src,
        rand_year_range=(2015, 2021)
    )

    print(f"[*] Packaging {len(raw_references)} raw references into dataset entries...")
    wrapped_dataset = make_dataset(raw_references)

    print("[*] Applying stochastic gradient policies (Tier 0 -> Tier 3)...")
    mutated_dataset = build_gradient_dataset(wrapped_dataset, mutator)

    print("[*] Baking formats and bitmasks...")
    bake_dataset(mutated_dataset)

    print(f"[*] Writing final mutated dataset to '{OUTPUT_MUTATED}'...")
    try:
        with open(OUTPUT_MUTATED, "w", encoding="utf-8") as f:
            json.dump(mutated_dataset, f, indent=2, ensure_ascii=False)
        print(f"[Success] Pipeline complete! File saved successfully.")
    except Exception as e:
        print(f"[!] Failed to write output file: {e}")
