
from tools.references.refdata import ReferenceComponent as RC

class ProtoSchemas:
    @staticmethod
    def realfakeconfidence(thing):
        return {
            "type": "object",
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "1 to 2 sentences outlining the reasoning behind your classification."       # This may help keep the model on track. 
                },
                "validity": {
                    "type": "boolean",
                    #"description": f"True if {thing} is real, false if {thing} is fake."
                    "description": f"True if {thing} is valid, false if {thing} is invalid."   # ! GENERATED or FAKE ?
                },
                "validity_confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    #"description": f"Confidence value (0.0 -> 1.0) of {thing} being real."   # Authentic, legitimate, exists? 
                    #"description": f"Confidence value (0.0 -> 1.0) in the classification 'real' for {thing}."   # Authentic, legitimate, exists? 
                    #"description": f"A floating point confidence value between 0.0 -> 1.0, denoting your confidence in {thing} being valid. High 'valid' confidence is 1.0, and high 'generated' confidence is 0.0."
                    "description": f"A floating point confidence value between 0.0 -> 1.0." #denoting your confidence in {thing} being valid."
                },
            },
            "required": ["reasoning", "validity", "validity_confidence"],
            "additionalProperties": False
        }

    @staticmethod
    def make_schema(properties):
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "reference_evaluation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": properties,
                    "required": list(properties.keys()),
                    "additionalProperties": False
                }
            }
        }

    # Include properties only for components present in a reference.
    @staticmethod
    def make_schema_properties(component_code = ~0):
        # Classify all components. Will trim this according to per reference specifics at some point (avoid confusion / forced hallucination)   @todo: track components in references, use that metadata to craft these specifically.
        properties = {
            RC.AUTHORS:             ProtoSchemas.realfakeconfidence("the author list"),
            RC.TITLE:               ProtoSchemas.realfakeconfidence("the article title"),
            RC.JOURNAL_NAME:        ProtoSchemas.realfakeconfidence("the journal"),
            RC.JOURNAL_VOLUME:      ProtoSchemas.realfakeconfidence("the journal volume"),
            RC.JOURNAL_ISSUE:       ProtoSchemas.realfakeconfidence("the journal issue"),
            RC.JOURNAL_PAGE:        ProtoSchemas.realfakeconfidence("the page number"),
            RC.ELOCATOR:            ProtoSchemas.realfakeconfidence("the elocator"),
            RC.PUBLICATION_DATE:    ProtoSchemas.realfakeconfidence("the publishing date"),
            RC.DOI:                 ProtoSchemas.realfakeconfidence("the doi"),
            RC.PMID:                ProtoSchemas.realfakeconfidence("the pmid"),
            RC.PMCID:               ProtoSchemas.realfakeconfidence("the pmcid"),
            "REFERENCE":            ProtoSchemas.realfakeconfidence("the reference")
        }
        return properties

if __name__ == "__main__":
    import json
    print(json.dumps(ProtoSchemas.make_schema(ProtoSchemas.make_schema_properties()), indent=2))


    """
    from orouterapi import *
    import requests
    import json

    p = process_response(requests.get(url="https://google.com", json=make_payload_completions(None, None, None)))
    print(json.dumps(p, indent=2))
    quit()


    classify = {
        "author":       ProtoSchemas.realfakeconfidence("the author list"),
        "author_order": ProtoSchemas.realfakeconfidence("the order of the author list"),
        "title":        ProtoSchemas.realfakeconfidence("the article title"),
        "journal":      ProtoSchemas.realfakeconfidence("the journal"),
        "vol":          ProtoSchemas.realfakeconfidence("the journal volume"),
        "iss":          ProtoSchemas.realfakeconfidence("the journal issue"),
        "page":         ProtoSchemas.realfakeconfidence("the page number"),
        "elocator":     ProtoSchemas.realfakeconfidence("the elocator"),
        "date":         ProtoSchemas.realfakeconfidence("the publishing date"),
        "doi":          ProtoSchemas.realfakeconfidence("the doi"),
        "pmid":         ProtoSchemas.realfakeconfidence("the pmid"),
        "pmcid":        ProtoSchemas.realfakeconfidence("the pmcid"),
        "REFERENCE":    ProtoSchemas.realfakeconfidence("the reference")
    }
    print(json.dumps(ProtoSchemas.make_schema(classify), indent=2), "\n\n")

    reference = "Penner M, Zwaigenbaum L, Piroddi N, Park S, Minhas RS, Singal D. Advances in supporting development in autistic children and youth. BMJ. 2026;393:e086562. Published 2026 Jun 10. doi:10.1136/bmj-2025-086562"
    model = "openai/gpt-oss-120b:free"
    #model = "openrouter/free:online"
    response = openrouter(model, reference, ProtoSchemas.make_schema(classify))

    print(json.dumps(response, indent=2))

    # If it failed, dump it out.
    if not response["output"]: print(response["full_json"]["choices"][0]["message"]["content"])
    """
