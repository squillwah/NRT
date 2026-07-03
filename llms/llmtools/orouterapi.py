
import os
import requests
import json
import time
from llmtools.help import log

def make_payload_responses(model, ref, schema): pass
def make_payload_completions(model, ref, schema):
    SYSTEMCONTEXT = "You are a citation classifier. Determine the authenticity of references and their individual components." #Your response must comply with the strict JSON schema."
    return {
        "model": model,
        "messages": [
            { "role": "system", "content": SYSTEMCONTEXT },
            { "role": "user", "content": ref }
        ],
        #"provider": { "order": ["google-ai-studio"], "require_parameters": True }, # Force providers that support response_format (all stated parameters)
        "response_format": schema,
        "plugins": [ { "id": "response-healing" } ] # Server-side mending of malformed JSON responses.
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

    return requests.post(url=f"https://openrouter.ai{endpoint}",
                         headers={"Authorization":f"Bearer {key}","Content-Type":"application/json" },
                         json=payload)

def parse_response(response, *, api="completions"):
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
                case "completions":
                    try: processed["content"] = json.loads(processed["response_json"]["choices"][0]["message"]["content"])
                    except Exception as e:
                        log("Couldn't parse json from choices/message/content: ", e, t="e")
                        input("Now would be the time to quit if something is wrong.")                               # @ Don't forget you put this here.
                        processed["content"] = processed["response_json"]["choices"][0]["message"]["content"]
                case "responses": processed["content"] = "......"
                case _: log(api, "typo stupid", t="e")
        except Exception as e:
            log("Couldn't even get text from [choices][0][message][content]: ", e, t="e")
    except Exception as e:
        log("Couldn't parse json from response: ", e, t="e")

    return processed

def trytryagain(request, kwargs, *, tries=3, wait=5):
    args = locals()
    retry = False
    response = request(**kwargs)
    if response.status_code != 200:
        log(f"Openrouter request error, status_code: {response.status_code}", t="e")
        retry = True
    # Catch upstream provider errors
    else:
        try:
            rjson = response.json() # May be fragile, JSON parsing errors or false positives etc.
            if "error" in rjson:
                log(f"Upstream error: {rjson["error"]}", t="e")
                retry = True
            else: log("Request success!")
        except Exception as e:
            log(f"Something terrible has happened. \n\n{e}\n\n{response.text}\n\n", t="e")
    if retry:
        if tries > 0:
            log(f"Trying again in {wait} seconds, {tries} tries left.", t="s")
            time.sleep(wait)
            args["tries"] = args["tries"] - 1
            response = trytryagain(**args)
        else: log(f"No tries left, giving up. Message: \n\n{response.text}\n\n", t="e")
    return response

if __name__ == "__main__":
    m = "openai/gpt-oss-20b:free"
    r = "Volk, R. J., Lewis, K. B., Smith, M., Carley, M., Barry, M. J., Bekker, H. L., H\u00e4rter, M., Hoffmann, T., McCaffery, K., Pignone, M., Steffensen, K. D., Sepucha, K., Thompson, R., Trevena, L., van der Weijden, T., Witteman, H. O., & Stacey, D. (2026). Updated International Patient Decision Aid Standards (IPDAS version 5.0): modified Delphi, evidence informed consensus process. BMJ (Clinical research ed.), 393, e088116. https://doi.org/10.1136/bmj-2025-088116"
    s = "thescemer"
    log(trytryagain(openrouter, {"model": m, "ref": r, "schema": s}).text)



