from litellm import completion
import os
from dotenv import load_dotenv
from dotenv import dotenv_values

#Deals with .env file
load_dotenv()
config = dotenv_values('.env')
api_key = config.get('GEMINI_API_KEY')

#API Key
os.environ["GEMINI_API_KEY"] = api_key

# Message to send all LLMs
message: str = "What is computer Science?"

print("\n +-----------------Start-----------------+")

# Request to Google Gemma-4-26b-a4b-it
response = completion(
  model="gemini/gemma-4-26b-a4b-it",
  messages=[{"role": "user", "content": f"{message}"}]
)
print(response.model)
print(response.choices[0].message.content)

print("\n +---------------Seperator---------------+")

# Request to  Gemini-2.5-flash
response = completion(
  model="gemini/gemini-2.5-flash",
  messages=[{"role": "user", "content":  f"{message}"}]
)
print(response.model)
print(response.choices[0].message.content)

print("\n +------------------End------------------+")