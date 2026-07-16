
from copy import deepcopy
from enum import Enum
from tools.references.refdata import ReferenceComponent
from tools.references.formats import FormatStyle, Formats
from tools.datasets.mutators import EntryMutator, SeverityClass

# Used for averaging of component mutation severities (in bake_dataset step).
# Weights are relative to eachother, and normalized to reference count on per reference basis (different references comprise varied assortments of components).
# Weights only take effect in the arbitrary holistic mutation severity classification. Only components present or mutated are considered in the weighted average.

# i dont think it makes a difference really, weather they be above 1 or below idk. do they gotta add up ? :(

# The way to actually do it is sum the priorities, and divide by that, not the total count of references

# How important should components (and their validity/mutation severity) be?
# Note: these weights strictly apply only when components are included. So: don't be afraid to set a high value for something that's both very important and optional (like a DOI).
COMPONENT_WEIGHTS = {
    ReferenceComponent.AUTHORS:          1.0,
    ReferenceComponent.TITLE:            2.0,
    ReferenceComponent.JOURNAL_NAME:     0.9,
    ReferenceComponent.JOURNAL_VOLUME:   0.45,
    ReferenceComponent.JOURNAL_ISSUE:    0.25,
    ReferenceComponent.JOURNAL_PAGE:     0.3,
    ReferenceComponent.ELOCATOR:         0.45,
    ReferenceComponent.PUBLICATION_DATE: 0.45,
    ReferenceComponent.DOI:              0.9,    # Pretty dang important, if it's included ... If absent, then not important. And the mutation type factors in too... So, an omission mutation on DOI has a severity of COMMON_VARIATION (low), to that'll lower the effect of weight here. Or vice versa. The number will be lower. Conversely, a doi hallucination has max severity of MAJOR_ERROR, so then the numbers would come at full force. The system is making sense?
    ReferenceComponent.URL_ABSTRACT:     0.75,
    ReferenceComponent.URL_DIRECT:       0.75,
    ReferenceComponent.PMCID:            0.75,
    ReferenceComponent.PMID:             0.75
}
    
    # @? Why is have less for just title but shouldnt have more cause it is half? Still not sure how weighting works... How say title always be worth half? Can even? Why? want?

# The layout of dataset entries.
def dsentry(rd, ID=None, ID_src=None):    #, *, ID=None):
    ref_data = deepcopy(rd)
    ref_metadata = ref_data.pop("_meta")
    return {
        "id": ID,               # Internal ID + original PMCID         IDs now stored as keys in the flat dataset dict. Categories can persist as per component/holistic tags (replacement for "suggested confidence" silliness)
        "id_source": ID_src,    # Changed from PMCID to relative dataset ID. Use dataset[entry["src_id"]]["data"]["pmcid"]
        "has_component": ref_metadata["has_component"],
        #"has_component_source": deepcopy(ref_metadata["has_component"]),    # Copy is kept for weighting of omitting mutations vs truly absent components (absent from source). ! May not be necessary if ["mut_severity"]["component"] infers this with NULLs. (never modified or always absent components default to NULL scores)
        "mut_code": 0b00000000, # Describes specific mutations.
        "mut_labels": [],
        "mut_severity": {
            "component": {  # Initialize component severity scores to True, leaving nonexistent ones (not in has_component) NULL. The NULL avoids caring about components that never existed and where never mutated (mutated components have an entry added to replace the NULL).
                comp: (
                    [ True, SeverityClass.NONE ] if ref_metadata["has_component"][comp] else None   # Default component scores to True, but set nonexistent components to NULL. True as in 'valid' (real, not erroneous), float for severity 0 -> 1 (most).
                ) for comp in ReferenceComponent
            },
            "holistic": {
                "complete": {
                    "score": None,  # Averaged scores are calculated on bake.   
                    "includes": []  # List of components included in score average calculation. Components used must be present in the reference data, with the excpetion of omitted components (but depending on the element, the omission severity may be quite low anyways). Used in evaluating LLM responses, seeing which components "contributed" to the reference they were given.
                },
                "format": {
                    style: {
                        "score": None,  # [True/False, SeverityClass]
                        "includes": []  # [authors, title, journal_name, ...]
                    } for style in FormatStyle    # Initialize style scores but leave NULL for bake.
                }
            },
        },
        "ref_citation": {       # All format styles are generated at baking step. 
            style: {
                "text": None,
                "components": None   # Include meta of which components are included in the reference text. ! This is the ultimate thing, shows what 'data' was actually given to the LLM after all this processing.
            } for style in FormatStyle
        },
        "ref_data": ref_data
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

def weighted_average_of_component_scores(scores):
    normalizer = sum(COMPONENT_WEIGHTS[c] for c in scores)
    weights = {c: COMPONENT_WEIGHTS[c]/normalizer for c in scores}
    avg_validity = all(s[0] for s in scores.values())               # ANDing all component validities together.
    avg_severity = sum(scores[c][1]*weights[c] for c in scores)     # Weighting component severities and summing.
    return [avg_validity, avg_severity]

# Compile references in format styles.
# Average mutation severity scores.
def bake_dsentry(entry):
    # 1 Render citations in all format styles.
    for style, citation in Formats.build_all(entry["ref_data"]).items():
        entry["ref_citation"][style]["text"] = citation
        #entry["ref_citation"][style]["components"] = {c: entry["has_component"][c] and Formats.components_in_style(style)[c] for c in ReferenceComponent}   # AND reference data has_component with components included in style, trimming any components that would never be included (never in style)
        entry["ref_citation"][style]["components"] = [c for c in ReferenceComponent if entry["has_component"][c] and Formats.components_in(style)[c]] # Alternatively, a list. Would have no Falses

    # 2 Average / weight severity scores     
    scores = {comp: score for comp, score in entry["mut_severity"]["component"].items() if score is not None}
    entry["mut_severity"]["holistic"]["complete"]["score"] = weighted_average_of_component_scores(scores)
    entry["mut_severity"]["holistic"]["complete"]["includes"] = weighted_average_of_component_scores(scores)
   
    # Mask components not included by default inside the reference style (for example, PMCIDs and URLs in our code for Harvard, APA, and vancouver). 
    # Because their ommitted by nature of the reference structure, it makes no sense to grade against them. There exists no case where the model would face the component in the specified reference style
    scores_fmt = {style: {c: s for c, s in scores.items() if Formats.components_in(style)[c]} for style in FormatStyle}     # Trim severity scores never present within FormatStyle
    for style, scores in scores_fmt.items():
        entry["mut_severity"]["holistic"]["format"][style]["score"] = weighted_average_of_component_scores(scores)
        entry["mut_severity"]["holistic"]["format"][style]["includes"] = list(scores.keys())
    
    
    entry["mut_labels"] = EntryMutator.explain_mutcode(entry["mut_code"])

    # If a component was present in the source reference, or had any mutation applied to it at all (such as a mutation which brought it into being), it has a severity score entry.
    # By this, we can go through the non NULL severity scores and just calculate their weighted average (according to normalized component priorities defined above).
    # The one excpetion to this, is that depending on the reference style some present components may have been excluded regardless, so we could be averaging with a bias from am absent component the chatbot would never have a chance to analyze (other than noting its absence).
    # So, with each built format comes a dict describing which components it tried to include (though this describes the template per format, not necessarily what is contained given what may have been ommitted. For that, just AND the true 'has_components' with the format style's)
    # Plus we'll also grade against some non mandatory components marked as (ommitted), but their severity score weights should be set accordingly so that it's within an 'acceptable' level of severity (very low).
    # Also, to avoid the error of flagging omissions on true nonexistent components (and thereby including in the average), omission mutations are not applied if the thing is already None or empty. (None vs empty depends on component, holdover from earlier implementation ideas)
    # It's all a bit meaningless honestly. When going component by component. The model would have to identify the original reference amid all the other clutter, and see that it doesn't line up. Quite the task. When the reference is so garbled to be entirely 'hallucinated', what really makes an 'unmutated' page number more 'real' than 'fake'?

# Bake mutation labels, reference formats, and suggested reference scores every entry in a dataset.
def bake_dataset(dataset):
    for entryID in dataset:
        bake_dsentry(dataset[entryID])


