import requests
from prompt_writer import generate_prompt
import json
import time
#import ollama
import os
#from dotenv import load_dotenv

from prompt_schemas import gen_schema


# The date thing in the context is stupid. 
# We can easily enable websearch and datetime fetching from OpenRouter, but that conflicts with structured responses.
# To do both, we will need to run two passes per reference. One that does the websearching and thinking, and the other which thinks again and encodes in into a structured response.
PROMPT_CONTEXT = """The date is 2026/06/28. You are a biomedical references verifier. Assess each component and examine the reference as a whole. Adhere to the strict structure response JSON schema."""
#Definitions of categories:
#1. Verified: The article exists, and the title plus key metadata match the database record. - Minor formatting differences are acceptable.
#2. Metadata Error: The article exists, but one or more fields are wrong, incomplete, abbreviated, or formatted differently. - The article can still be confidently identified.
#3. Serious Metadata Error: The title or other major fields are wrong, but the DOI or PMID correctly points to a real article. - Not fabricated if the DOI/PMID identifies a real article.
#4. Plausible Fabricated: The claimed title cannot be matched to any real article after reasonable search. - Real authors, real journals, or plausible topics are not enough to prove the article exists.
#5. Needs Human Review: The evidence is mixed, weak, or ambiguous. - Use this when there are partial title matches, missing/conflicting DOI or PMID, or multiple possible matches."""


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

# Should we use the context_header / classifications?
# Doing so kinda removes this from a "real-world" type scenario (people just asking bots if refs are real), but we're pretty far from that already with the structured response format.
def payload_template(reference, model, schema, context, *, search=True, datetime=True):
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


# For testing
#print(json.dumps(schema, indent=2))
schema = gen_schema(verify=FOR_VERIFICATION, classify=FOR_CLASSIFICATION)
testmod = "openai/gpt-oss-120b:free" #"openrouter/free"   # Auto choose one that supports structured responses + netsearch. For testing.      #"openai/gpt-oss-20b:free"
testref = "Penner M, Zwaigenbaum L, Piroddi N, Park S, Minhas RS, Singal D. Advances in supporting development in autistic children and youth. BMJ. 2026;393:e086562. Published 2026 Jun 10. doi:10.1136/bmj-2025-086562"


payload = payload_template(testref, testmod, schema, PROMPT_CONTEXT, search=True, datetime=True)
print(json.dumps(payload, indent=2))
print("\n\n\n")
response = requests.post(url="https://openrouter.ai/api/v1/chat/completions",
                         headers={ "Authorization": f"Bearer {os.environ["key"]}", "Content-Type": "application/json" },
                         json=payload)



data = None
try:
    data = response.json()
    print(json.dumps(data, indent=2))
except:
    print(response.content)
print("\n\n\n")
try:
    print(json.dumps(json.loads(data["choices"][0]["message"]["content"])))
except:
    print(response.content)
    pass
quit()






















"""
def openrouter_all_call(header_prompt, citation):

    print("Starting API Requests")
    time.sleep(1)

    results = []
    # jsonObject = openrouter_accessor(header_prompt, citation, "google/gemma-4-26b-a4b-it:free")
    # results.append(jsonObject)
    # time.sleep(1)
    # print("1 Done")

    # jsonObject = openrouter_accessor(header_prompt, citation, "nex-agi/nex-n2-pro:free")
    # results.append(jsonObject)
    # time.sleep(1)
    # print("2 Done")

    # jsonObject = openrouter_accessor(header_prompt, citation, "openrouter/owl-alpha")
    # results.append(jsonObject)
    # time.sleep(1)
    # print("3 Done")

    # jsonObject = openrouter_accessor(header_prompt, citation, "nvidia/nemotron-3-super-120b-a12b:free")
    # results.append(jsonObject)
    # time.sleep(1)
    # print("4 Done")

    jsonObject = openrouter_accessor(header_prompt, citation, "openai/gpt-oss-20b:free")
    results.append(jsonObject)
    time.sleep(1)
    print("5 Done")

    # jsonObject = openrouter_accessor(header_prompt, citation, "cognitivecomputations/dolphin-mistral-24b-venice-edition:free")
    # results.append(jsonObject)
    # time.sleep(1)

    return results

respone = requests.post(url="https://openrouter.ai/api/v1/chat/completions",
                        headers={ "Authorization": f"Bearer {api_key}", "Content-Type": "application/json" },
                        json=payload)


def openrouter_accessor(header, citation, model):
    #api_key = os.getenv("OPENROUTER_API_KEY")


    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        # To use a BYOK model, simply change the chat/completions to byok/<api-model-key>
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": (header + citation)
                                #header +
                                #"\n\n=== CATEGORIES & DEFINITIONS ===\n"
                                #"1. Verified: The article exists, and the title plus key metadata match the database record. - Minor formatting differences are acceptable.\n"
                                #"2. Metadata Error: The article exists, but one or more fields are wrong, incomplete, abbreviated, or formatted differently. - The article can still be confidently identified.\n"
                                #"3. Serious Metadata error: The title or other major fields are wrong, but the DOI or PMID correctly points to a real article. - Not fabricated if the DOI/PMID identifies a real article.\n"
                                #"4. Plausible fabricated: The claimed title cannot be matched to any real article after reasonable search. - Real authors, real journals, or plausible topics are not enough to prove the article exists.\n"
                                #"5. needs human review: The evidence is mixed, weak, or ambiguous. - Use this when there are partial title matches, missing/conflicting DOI or PMID, or multiple possible matches.\n"
                                #"\n=== CITATION TO VALIDATE ===\n" +
                                #(citation if isinstance(citation, str) else next(iter(citation.values()), ""))),
                }
            ],
            "response_format": schema,

        }
    )

  # 1. Convert the raw API HTTP response into a Python dictionary
    try:
        api_data = response.json()
        print(json.dumps(api_data, indent=2))
    except:
        print(response.content)
  # 2. Extract the stringified content out of the nested dictionary structure
    try:
        raw_content = api_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        print(f"API Error Response: {api_data}")
        raise RuntimeError(f"Failed to extract text from API response: {e}")

    try:
        response_dict = json.loads(raw_content)
        response_dict["model"] = api_data["model"]
        response_dict["reasoning_tokens"] = api_data["usage"]["completion_tokens_details"]["reasoning_tokens"]
    except json.JSONDecodeError:
        print("WARNING: Response was not valid JSON, returning raw text")
        response_dict = {"model": api_data["model"], "message": raw_content}

    return response_dict

if __name__ == "__main__":
    #input_header = generate_prompt()
    input_citation = {"citation1": "Penner M, Zwaigenbaum L, Piroddi N, Park S, Minhas RS, Singal D. Advances in supporting development in autistic children and youth. BMJ. 2026;393:e086562. Published 2026 Jun 10. doi:10.1136/bmj-2025-086562"}
    jsonObject = openrouter_accessor(CLASSIFIER_DESCRIPTION_HEADER, input_citation["citation1"], "openai/gpt-oss-20b:free")
    print("\n\n")
    print(json.dumps(jsonObject, indent=2))
    #print(openrouter_all_call(input_header, input_citation))
"""
