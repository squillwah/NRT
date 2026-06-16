import requests
from prompt_writer import generate_prompt
import json

response_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "model_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "message": {"type": "string"}
            },
            "required": ["model", "message"]
        }
    }
}

def openrouter_accessor(header, citation):
  response = requests.post(
   url="https://openrouter.ai/api/v1/chat/completions",
   headers = {
    "Authorization": "Bearer <ADD_OPENROUTER_API_KEY_HERE>",
    "Content-Type": "application/json"
   },
   json={
    "model": "google/gemma-4-26b-a4b-it:free",
    "messages": [
      {
       "role": "user",
        "content": header + "\n" + (citation if isinstance(citation, str) else next(iter(citation.values()), ""))      }
    ],
       "response_format": response_schema
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
 print(openrouter_accessor(input_header, input_citation))
