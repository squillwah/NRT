
from copy import deepcopy
from enum import Enum
from tools.references.refdata import ReferenceComponent
from tools.references.formats import FormatStyle, Formats
from tools.datasets.mutators import EntryMutator, SeverityClass

# Used for averaging of component mutation severities (in bake_dataset step).
# Weights are relative to eachother, and normalized to reference count on per reference basis (different references comprise varied assortments of components).
# Weights only take effect in the arbitrary holistic mutation severity classification. Only components present or mutated are considered in the weighted average.
class ComponentWeights(float, Enum):
    AUTHORS = 10
    TITLE = 10
    JOURNAL_NAME = 10
    JOURNAL_VOLUME = 5
    JOURNAL_ISSUE = 3
    JOURNAL_PAGE = 3
    ELOCATOR = 3
    PUBLICATION_DATE= 3
    DOI = 8
    URL_ABSTRACT = 5
    URL_DIRECT = 5
    PMCID = 7
    PMID = 7

# The layout of dataset entries.
def dsentry(rd, ID=None, ID_src=None):    #, *, ID=None):
    ref_data = deepcopy(rd)
    ref_metadata = ref_data.pop("_meta")
    return {
        "id": ID,               # Internal ID + original PMCID         IDs now stored as keys in the flat dataset dict. Categories can persist as per component/holistic tags (replacement for "suggested confidence" silliness)
        "id_source": ID_src,    # Changed from PMCID to relative dataset ID. Use dataset[entry["src_id"]]["data"]["pmcid"]
        "has_component": ref_metadata["has_component"],
        "has_component_source": deepcopy(ref_metadata["has_component"]),    # Copy is kept for weighting of omitting mutations vs truly absent components (absent from source). ! May not be necessary if ["mut_severity"]["component"] infers this with NULLs. (never modified or always absent components default to NULL scores)
        "mut_code": 0b00000000, # Describes specific mutations.
        "mut_labels": [],
        "mut_severity": {
            "entire": [True, SeverityClass.REAL],   # Default holistic score to True
            "format": {
                style: None for style in FormatStyle    # Initialize style scores but leave NULL for bake.
            },
            "component": {
                comp: ([True, SeverityClass.REAL] if ref_metadata["has_component"][comp] else None) for comp in ReferenceComponent  # Default component scores to True, but set nonexistent components to NULL
            }
        },
        "reference": {},        # All format styles generated at baking step. 
        "data": ref_data
    }

# Create a set of set entries from a list of reference data.
# 'duplicate' specifies how many copies of the source should be included
def make_dataset(refdata_source, duplicate=0):
    dataset = {}
    source_size = len(refdata_source)
    for i, refdata in enumerate(refdata_source):
        source_id = i
        dataset[source_id] = dsentry(refdata, ID=source_id, ID_src=None)
        for j in range(1, duplicate+1):                         # Extend duplicates with source IDs attached (0, None) ... (99, None) | (100, 0), (101, 1), etc
            duplicate_id = source_id + j*source_size
            dataset[duplicate_id] = dsentry(refdata, ID=duplicate_id, ID_src=source_id)
    return dataset

# Compile references in format styles.
# Average mutation severity scores.
def bake_dsentry(entry):
    entry["reference"] = Formats.build_all(entry["data"])
#    for form in entry["format"]    @TODO AND with refdata COMPONENTS (once that's synced with mutations)

# Should severity be higher or lower numbers? Probably higher, since it's multiplied by weight. Although it might not matter either way, as long as consistent. Higher is more intuitive though.
    entry["mut_labels"] = EntryMutator.explain_mutcode(entry["mut_code"])
    # Averaging holistic score
    c_scores = {component: entry["mut_severity"]["component"][component] for component in ReferenceComponent if entry["mut_severity"]["component"][component]} # Components with existing scores in the dsentry.
    score = entry["mut_severity"]["entire"]
    classes, confidences = zip(*[c_scores[c] for c in c_scores])    # Lists of all classification bools and confidence values for all components.
    score[0] = classes and all(classes)                             # AND every class           @TODO May want to weight these somehow? Or should even the tiniest typo make it "false"? If so, then the binary score means a slightly different thing than confidence. Probably good that way? Maybe not, a confusing case would be a False (invalid) class due to a type but a very high (.95) confidence value. It would make sense on the component level (since we shouldn't set default conf values above .5), but not when maintaining that negative bool for the average. ANDing booleans is not the same as averaging. Do we even need the True/False at this step? Probably, something to mark the mutation. Otherwise setting the suggested confidences will be tricky and precise, we open ourselves up to clearly mutated/hallucinated references being marked True when the average works out > .5
    score[1] = sum(confidences)/len(confidences)                    # Average all confidences   ... probably need a zero check here ...
    # @TODO Averaging the formatted scores (exlcuding absent components)
    # @TODO Doing the averaging logic different in a way that doesn't bias from component count? ?
    # Note the getting of the format score thing is really only relevant if we really care to evaluate model responses within our specific arbitrary framework. It's not the big focus.
    # It's all a bit meaningless honestly. When going component by component. The model would have to identify the original reference amid all the other clutter, and see that it doesn't line up. Quite the task. When the reference is so garbled to be entirely 'hallucinated', what really makes an 'unmutated' page number more 'real' than 'fake'?

#    for style in FormatStyles:
#        score = entry["scores"]["byformat"][style]
#        classes, confidences = zip(*[c_scores[c] for c in c_scores if entry["format"][style]["components"][c])  # Do not include scores absent from the formatted reference (detailed by "components" element with the formatted string.
#        score[0] = score[0] and all(c_scores[0])
#        score[1] = sum(c_scores[1])/len(c_scores[1])

# Bake mutation labels, reference formats, and suggested reference scores every entry in a dataset.
def bake_dataset(dataset):
    for entryID in dataset:
        bake_dsentry(dataset[entryID])


