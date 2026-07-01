
import os
import requests
import json

def make_payload_responses(model, ref, schema): pass
def make_payload_completions(model, ref, schema):
    SYSTEMCONTEXT = "You are a citation classifier. Determine the authenticity of references and their individual components. Your response must comply with the strict JSON schema."
    return {
        "model": model,
        "messages": [
            { "role": "system", "content": SYSTEMCONTEXT },
            { "role": "user", "content": ref }
        ],
        "response_format": schema,
        "plugins": [ { "id": "response-healing" } ]     # Server-side mending of malformed JSON responses.
    }


# Should this do processing as it does, or just return the response object (throw it down the road)?
def openrouter(model, ref, schema, *, api="completions", key=os.environ["THEKEY"]):
    payload = None
    endpoint = None
    match api:
        case "completions":
            payload = make_payload_completions(model, ref, schema)
            endpoint = "/api/v1/chat/completions"
        case "responses":
            payload = make_payload_responses(model, ref, schema)
            endpoint = "/api/v1/responses"
        case _: print(api, "typo stupid")

    return requests.post(url=f"https://openrouter.ai{endpoint}",
                         headers={"Authorization":f"Bearer {key}","Content-Type":"application/json" },
                         json=payload)

def process_response(response, *, api="completions"):
    processed = {
        "request_json": json.loads(response.request.body.decode("utf-8")),
        "response_text": response.text,
        "response_json": None,
        "content": None
    }
    try:
        processed["response_json"] = response.json()
        try:
            match api:
                case "completions": processed["content"] = json.loads(processed["full_json"]["choices"][0]["message"]["content"])
                case "responses": processed["content"] = "......"
                case _: print(api, "typo stupid")
        except requests.exceptions.JSONDecodeError as e:
            print(" !!! couldn't parse json from choices/message/content: ", e)
    except requests.exceptions.JSONDecodeError as e:
        print(" !!! couldn't parse json from response: ", e)

    return processed
