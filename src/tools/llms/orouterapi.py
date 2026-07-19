
import os
import requests
import json
import time
from tools.help import log

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
        "require_parameters": True, 
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

    # Recording time benchmark
    t = time.perf_counter()
    response = requests.post(url=f"https://openrouter.ai{endpoint}",
                             headers={"Authorization":f"Bearer {key}","Content-Type":"application/json" },
                             json=payload)
    t = time.perf_counter() - t     # End time minus start time

    return response, t

def parse_response(response): #, *, api="completions"):
    processed = {
        "request": json.loads(response.request.body.decode("utf-8")),
        "response": None,
        "result": None
    }
    try: processed["response"] = response.json()
    except Exception as e:
        log("Couldn't parse json from response: ", e, t="e")
        log("Saving response as plaintext, result as null", t="e")
        processed["response"] = response.text
        processed["result"]: None
    else:
        try: processed["result"] = json.loads(processed["response"]["choices"][0]["message"]["content"])
        except Exception as e:
            #input("Now would be the time to quit if something is wrong.")                               # @ Don't forget you put this here.
            log("Couldn't parse json from response[choices][0][message][content] (does the model support response_format?): ", e, t="e")
            try: processed["result"] = processed["response"]["choices"][0]["message"]["content"]
            except Exception as e: log("Couldn't even get text from response[choices][0][message][content]: ", e, t="e")
    return processed

def trytryagain(request, kwargs, *, tries=3, wait=5):
    args = locals()
    retry = False

    response, t = request(**kwargs)
    
    if response.status_code != 200:
        log(f"Openrouter request error, status_code: {response.status_code}", t="e")
        retry = True
    else:
        # Catch upstream provider errors
        try:
            rjson = response.json() # May be fragile, JSON parsing errors or false positives etc.
            if "error" in rjson:
                log(f"Upstream error: {rjson["error"]}", t="e")
                retry = True
            else: log("Request success!", t="s")
        except Exception as e:
            log(f"Something terrible has happened. \n\n{e}\n\n{response.text}\n\n", t="e")
    
    if retry:
        if tries > 0:
            log(f"Trying again in {wait} seconds, {tries} tries left.", t="s")
            time.sleep(wait)
            args["tries"] = args["tries"] - 1
            response, t = trytryagain(**args)
        else: log(f"No tries left, giving up. Message: \n\n{response.text}\n\n", t="e")
    
    return response, t # TODO: return time here.

# Or have another wrapper function around openrouter, and send that to trytryagain. Probably best that way.

if __name__ == "__main__":
    m = "openai/gpt-oss-20b:free"
    r = "Volk, R. J., Lewis, K. B., Smith, M., Carley, M., Barry, M. J., Bekker, H. L., H\u00e4rter, M., Hoffmann, T., McCaffery, K., Pignone, M., Steffensen, K. D., Sepucha, K., Thompson, R., Trevena, L., van der Weijden, T., Witteman, H. O., & Stacey, D. (2026). Updated International Patient Decision Aid Standards (IPDAS version 5.0): modified Delphi, evidence informed consensus process. BMJ (Clinical research ed.), 393, e088116. https://doi.org/10.1136/bmj-2025-088116"
    s = "thescemer"
    log(trytryagain(openrouter, {"model": m, "ref": r, "schema": s}).text)



