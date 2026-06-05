
from google import genai
from google.genai.errors import ClientError
import time

client = genai.Client()

print("\nFetching gemini models...")
models = [m.name for m in client.models.list() if "generateContent" in m.supported_actions] # 'generateContent' is basic text generation
for m in models: print(f"- {m}")


print("\nChecking free tier support...")
responses = []
free_models = []
timeout_occured = False
for m in models:
    try: responses.append(client.models.generate_content(model=m, contents="Is your API free? Response Y or N."))
    except ClientError as e:
        # If timeout, wait and retry. 
        # successive_timeouts = -1
        # while e.code == 429:
        #     # Grab timeout from error message. Round up, double for each successive timeout.
        #     successive_timeouts = successive_timeouts + 1
        #     timeout = (int(float(e.message[e.message.rfind(" "):-2]))+1) * 2**successive_timeouts
        #     print(f"Quota timeout with {m}, waiting {timeout}s")
        #     time.sleep(timeout)
        #     try: responses.append(client.models.generate_content(model=m, contents="Is your API free? Response Y or N."))
        #     except ClientError as e2: e = e2
        # If other error, skip model. 
        if e.code == 429:
            print(f"Quota timeout with {m}, skipping.") # Some models refuse to work even with waiting. Just skip for now.
            continue
        if e.code != 429:
            print(f"! Error {e.code} with {m}, skipping: {e.response} | {e.status} | {e.message}")
            continue
    print(f"{m} : '{responses[-1].text}'")
    free_models.append(m)

print("\nFree models: ");
for m in free_models: print(f"- {m}")



