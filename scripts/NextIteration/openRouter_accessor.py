import requests
from prompt_writer import generate_prompt
import json
import time
import ollama
import os
from dotenv import load_dotenv

load_dotenv()
response_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "citation_validation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {

                "author": {
                    "type": "string",
                    "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
                    "description": "Verification status of author name(s) and attribution"
                },
                "confidence_author": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Confidence score (0-100) for the author verification"
                },
                "journal": {
                    "type": "string",
                    "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
                    "description": "Verification status of the journal name and indexing"
                },

                "confidence_journal": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Confidence score (0-100) for the journal verification"
                },

                "publish_date": {
                    "type": "string",
                    "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
                    "description": "Verification status of publication date accuracy"
                },

                "confidence_of_the_publish_date": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Confidence score (0-100) for the citation's publishing date verification"
                },

                "author_order": {
                    "type": "string",
                    "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
                    "description": "Whether the author order matches the original source"
                },

                "confidence_of_the_author_order": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Confidence score (0-100) for the citation's author order verification"
                },

                "publisher": {
                    "type": "string",
                    "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
                    "description": "Verification status of publisher name and imprint"
                },

                "confidence_of_the_publisher": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Confidence score (0-100) for the citation's publisher verification"
                },

                "overall": {
                    "type": "string",
                    "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
                    "description": "Overall assessment of the citation's authenticity"
                },
                "confidence_overall": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Confidence score (0-100) for the overall assessment"
                }
            },
            "required": ["overall", "confidence_overall", "author", "journal", "publish_date", "author_order", "publisher", "confidence_of_the_publisher", "confidence_of_the_author_order", "confidence_journal", "confidence_of_the_publish_date", "confidence_author"],
            "additionalProperties": False
        }
    }
}

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



def openrouter_accessor(header, citation, model):
    api_key = os.getenv("OPENROUTER_API_KEY")

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
                    "content": (header +
                                "\n\n=== CATEGORIES & DEFINITIONS ===\n"
                                "1. Verified: The article exists, and the title plus key metadata match the database record. - Minor formatting differences are acceptable.\n"
                                "2. Metadata Error: The article exists, but one or more fields are wrong, incomplete, abbreviated, or formatted differently. - The article can still be confidently identified.\n"
                                "3. Serious Metadata error: The title or other major fields are wrong, but the DOI or PMID correctly points to a real article. - Not fabricated if the DOI/PMID identifies a real article.\n"
                                "4. Plausible fabricated: The claimed title cannot be matched to any real article after reasonable search. - Real authors, real journals, or plausible topics are not enough to prove the article exists.\n"
                                "5. needs human review: The evidence is mixed, weak, or ambiguous. - Use this when there are partial title matches, missing/conflicting DOI or PMID, or multiple possible matches.\n"
                                "\n=== CITATION TO VALIDATE ===\n" +
                                (citation if isinstance(citation, str) else next(iter(citation.values()), ""))),
                }
            ],
            "response_format": response_schema,

        }
    )

  # 1. Convert the raw API HTTP response into a Python dictionary
    api_data = response.json()
    print(api_data)
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
 input_header = generate_prompt()
 input_citation = {"citation1": "Penner M, Zwaigenbaum L, Piroddi N, Park S, Minhas RS, Singal D. Advances in supporting development in autistic children and youth. BMJ. 2026;393:e086562. Published 2026 Jun 10. doi:10.1136/bmj-2025-086562"}
 print(openrouter_all_call(input_header, input_citation))
