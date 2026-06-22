import requests
from prompt_writer import generate_prompt
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
response_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "model_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},

                "overall": {
                    "type" : "string",
                    "description" : "Yes or no; real citation"
                },

                "author": {
                    "type": "string",
                    "description" : "Yes or no; real author"
                },

                "journal": {
                    "type" : "string",
                    "description" : "Yes or no; real journal"
                },

                "publish_date": {
                    "type" : "string",
                    "description" : "Yes or no; correct publish date"
                },

                "author_order": {
                    "type" : "string",
                    "description" : "Yes or no; correct author order"
                },

                "publisher": {
                    "type" : "string",
                    "description" : "Yes or no; correct publisher"
                },

                "percentage_of_confidence": {
                    "type" : "number",
                    "description" : "percentage of confidence"
                }


            },
            "required": ["model", "overall", "author", "journal", "publish_date", "author_order", "publisher", "percentage_of_confidence"],
            "additionalProperties": False
        }
    }
}

def openrouter_all_call(header_prompt, citation):

    print("Starting API Requests")
    time.sleep(1)

    results = []
    jsonObject = openrouter_accessor(header_prompt, citation, "google/gemma-4-26b-a4b-it:free")
    results.append(jsonObject)
    time.sleep(1)
    print("1 Done")

    # jsonObject = openrouter_accessor(header_prompt, citation, "nex-agi/nex-n2-pro:free")
    # results.append(jsonObject)
    # time.sleep(1)
    # print("2 Done")

    jsonObject = openrouter_accessor(header_prompt, citation, "openrouter/owl-alpha")
    results.append(jsonObject)
    time.sleep(1)
    print("3 Done")

    jsonObject = openrouter_accessor(header_prompt, citation, "nvidia/nemotron-3-super-120b-a12b:free")
    results.append(jsonObject)
    time.sleep(1)
    print("4 Done")

    jsonObject = openrouter_accessor(header_prompt, citation, "openai/gpt-oss-20b:free")
    results.append(jsonObject)
    time.sleep(1)
    print("5 Done")

    '''jsonObject = openrouter_accessor(header_prompt, citation, "cognitivecomputations/dolphin-mistral-24b-venice-edition:free")
    results.append(jsonObject)
    time.sleep(1)'''

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
                    "content": header + "\n" + (
                        citation if isinstance(citation, str) else next(iter(citation.values()), ""))}
            ],
            "response_format": response_schema,

            "tools": [
                {"type": "openrouter:datetime"}
            ]
        }
    )

  # 1. Convert the raw API HTTP response into a Python dictionary
    api_data = response.json()

  # 2. Extract the stringified content out of the nested dictionary structure
    try:
        raw_content = api_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        print(f"API Error Response: {api_data}")
        raise RuntimeError(f"Failed to extract text from API response: {e}")

    try:
        response_dict = json.loads(raw_content)
    except json.JSONDecodeError:
        print("WARNING: Response was not valid JSON, returning raw text")
        response_dict = {"model": api_data["model"], "message": raw_content}

    return response_dict

if __name__ == "__main__":
 input_header = generate_prompt()
 input_citation = {"citation1": "Penner M, Zwaigenbaum L, Piroddi N, Park S, Minhas RS, Singal D. Advances in supporting development in autistic children and youth. BMJ. 2026;393:e086562. Published 2026 Jun 10. doi:10.1136/bmj-2025-086562"}
 print(openrouter_all_call(input_header, input_citation))
