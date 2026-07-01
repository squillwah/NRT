
class ProtoSchemas:
    @staticmethod
    def realfakeconfidence(thing):
        return {
            "type": "object",
            "properties": {
                "classification": {
                    "type": "boolean",
                    #"description": f"True if {thing} is real, false if {thing} is fake."
                    "description": f"True if {thing} is real, false if {thing} is generated."   # ! GENERATED or FAKE ?
                },
                "confidence_real": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    #"description": f"Confidence value (0.0 -> 1.0) of {thing} being real."   # Authentic, legitimate, exists? 
                    "description": f"Confidence value (0.0 -> 1.0) of {thing} being real."   # Authentic, legitimate, exists? 
                },
                "confidence_fake": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    #"description": f"Confidence value (0.0 -> 1.0) of {thing} being fake."   # Artificial, fabricated, hallucinated?
                    "description": f"Confidence value (0.0 -> 1.0) of {thing} being generated."   # Artificial, fabricated, hallucinated?
                }
            },
            "required": ["classification", "confidence_real", "confidence_fake"],
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

if __name__ == "__main__":
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
