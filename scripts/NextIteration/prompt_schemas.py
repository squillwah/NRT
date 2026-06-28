
# The structure of our respones.

# What do we want out of our LLMs?
#  - Holistic
#    - Is this references real or fake? (Yes/No)                (Should we use more precise wording? Authentic vs Fabricated, Trustworthy vs Suspicious?) We could do a small trial with each, to see how results compare. @todo: Experiment. 
#    - How real is this reference, as a percentage?             (Kind of same as confidence score. We should be thinking precisely about the wording, how will our framing affect their outputs? Other wordings could be 'how authentic is this reference 0-100', etc.)
#    - What classification does this reference fall under?      (If we're doing the classification thing. Even still, we need to better define them cause Pan's preliminaries are fuzzy.
#  - Component-wise
#    - Is this <component> (authors, title, etc.) real or fake? (Should we use the word 'hallucinated', or does that carry too much baggage?)
#    - How likely is it that this component is real (0-100)?

# This would yield an output of one binary (Y/N) classification and one continuous (%) probability of authenticty for each component and the ref as a whole.        (@Consider: it will be interesting to see how the sum of component-wise classifications/predictions compares to the holistic. Is there consistency or is it all made up?) 

# ! The difference between confidence scores and a real/fake gradient would be to what the value is relating.
# A confidence score would represent how much the LLM thinks it's answer is right (I am 95% confident that my assesment <real/fake> of this <reference/component> is correct!)
# Whereas the ends of a real/fake score would remain consistent between each response (The chance that this <reference/component> is real is 95%.)

# !!! Positive or negative logic? Should we be doing "True"/100% for real, or "True"/100% for fabricated?

# More documentation on structured outputs:
# https://developers.openai.com/api/docs/guides/structured-outputs
# https://json-schema.org/docs

def protoschema_verify(thing):   #, *, override_binary=None, override_continuous=None):     Could do a thing like this if it becomes needed to alter the prompts.
    return {
        "type": "object",
        "properties": {
            "binary": {
                "type": "boolean",
                "description": f"True if {thing} is real."          # Or 'False if this is <fabricated/hallucinated>'?, 'True if this is authentic'? What do we mean by "real"? How much of "real"'s interpretation do we want to leave up to the LLM?          How about just "correct"?
            },
            "continuous": {
                "type": "number",
                "minimum": 0,   # 0-1 avoids confusion of 0.99 vs 99 
                "maximum": 1,
                "description": f"The percent probability that {thing} is real." # Is 'probability' the right framing?
            }
        },
        "required": ["binary", "continuous"],
        "additionalProperties": False
    }
def protoschema_classify(thing):
    return {
        "type": "object",
        "properties": {
            "class": {
                "type": "string",
                "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],     # !!! An important question: How much of the JSON schema can the chatbot "see" at once? Will the context of other properties in the schema have an effect? By precedence?
                "description": f"Classification of {thing}."
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": f"Percentage of confidence in the classification of {thing}."
            }
        },
        "required": ["class", "confidence"],
        "additionalProperties": False
    }

# Order of elements in schema follows order of lists and strings in lists.
def gen_schema(verify, classify):
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "citation_validation",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    f"{thing}_v": protoschema_verify(verify[thing]) for thing in verify         # Using thing names as labels.
                } | {
                    f"{thing}_c": protoschema_classify(classify[thing]) for thing in classify
                },
                "required": [f"{thing}_v" for thing in verify] + [f"{thing}_c" for thing in classify],
                "additionalProperties": False
            }
        }
    }

# Should we use the context_header / classifications?
# Doing so kinda removes this from a "real-world" type scenario (people just asking bots if refs are real), but we're pretty far from that already with the structured response format.
def gen_payload(reference, model, schema, context, *, search=True, datetime=True):
    toolgles = (("openrouter:web_search", search),          #zip((search, datetime), ("openrouter:web_search", "openrouter:datetime")) 
                ("openrouter:datetime", datetime))
    return {
        "model": model,
        "messages": [
            { "role": "system", "content": context },    # https://openrouter.ai/docs/api/reference/overview What about the 'name' one?
            { "role": "user", "content": reference }
        ],
        "tools": [{ "type": tool } for tool, toggle in toolgles if toggle],     # https://openrouter.ai/docs/guides/features/server-tools/overview
        "response_format": schema                                               # We can also define local tools, if that becomes useful. https://openrouter.ai/docs/guides/features/tool-calling
    }


# The date thing in the context is stupid. 
# We can easily enable websearch and datetime fetching from OpenRouter, but that conflicts with structured responses.
# To do both, we will need to run two passes per reference. One that does the websearching and thinking, and the other which thinks again and encodes in into a structured response.
PROMPT_CONTEXT = """The date is 2026/06/28. You are a biomedical references verifier. Assess each component and examine the reference as a whole. Adhere to the strict structure response JSON schema.
Definitions of categories:
1. Verified: The article exists, and the title plus key metadata match the database record. - Minor formatting differences are acceptable.
2. Metadata Error: The article exists, but one or more fields are wrong, incomplete, abbreviated, or formatted differently. - The article can still be confidently identified.
3. Serious Metadata Error: The title or other major fields are wrong, but the DOI or PMID correctly points to a real article. - Not fabricated if the DOI/PMID identifies a real article.
4. Plausible Fabricated: The claimed title cannot be matched to any real article after reasonable search. - Real authors, real journals, or plausible topics are not enough to prove the article exists.
5. Needs Human Review: The evidence is mixed, weak, or ambiguous. - Use this when there are partial title matches, missing/conflicting DOI or PMID, or multiple possible matches."""

# Dict of internal component tags (in schema/response) against descriptions of components (for prompt insertion, see protoschema templates).
FOR_VERIFICATION = {
    "author": "the author list",        # True if {the author list} is real. / Probability that {the author list} is real. / Classification of {the author list}.
    "author_order": "the order of the author list",
    "title": "the article title",
    "journal": "the journal",       # Should we make the distinction of "journal name" specifically?
    "vol": "the journal volume",
    "iss": "the journal issue",
    "page": "the page number",              # !!!! Consider: not all formatted references will have all these components. Should we do some special tailoring of each schema to reflect that? May involve baking a schema for each response, as even within formats some data can be missing. Still the final output (grids?) should probably remain consistant, ig just put nulls or something in the empty spots?
    "elocator": "the elocator",             # If a ref has an elocator, it will not have a page number. We could merge these together, into just "the page number or elocator". @todo: probably that.
    "date": "the publishing date",
    "doi": "the doi",               # Should we split prefix / suffix?
    "pmid": "the pmid",
    "pmcid": "the pmcid",
    "REFERENCE": "the reference"    # Verify and classify the reference (as a whole).
}
FOR_CLASSIFICATION = { "REFERENCE": "the reference" }

# For testing
if __name__ == "__main__":
    import json
    import os
    import requests

#    testmod = #"openai/gpt-oss-120b:free" #"openrouter/free"   # Auto choose one that supports structured responses + netsearch. For testing.      #"openai/gpt-oss-20b:free"
    testmod = "openrouter/free"
    testref = "Penner M, Zwaigenbaum L, Piroddi N, Park S, Minhas RS, Singal D. Advances in supporting development in autistic children and youth. BMJ. 2026;393:e086562. Published 2026 Jun 10. doi:10.1136/bmj-2025-086562"

    schema = gen_schema(verify=FOR_VERIFICATION, classify=FOR_CLASSIFICATION)
    payload = gen_payload(testref, testmod, schema, PROMPT_CONTEXT, search=True, datetime=True)
    print(json.dumps(payload, indent=2))
    print("\n\n\n")

    response = requests.post(url="https://openrouter.ai/api/v1/chat/completions",
                             headers={ "Authorization": f"Bearer {os.environ["key"]}", "Content-Type": "application/json" },
                             json=payload)
    data = None
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except: print(response.content)
    print("\n\n\n")
    try: print(json.dumps(json.loads(data["choices"][0]["message"]["content"])))
    except: print(response.content)
