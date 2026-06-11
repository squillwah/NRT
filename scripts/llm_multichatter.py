import requests
from os import environ
from pmc_grabber import grab_articles

# Export your keys in corresponding environment vars 
# (or just replace environ[key] in this dict)
KEYS = {"GEMINI": "", "OPENAI":""}

#articles = grab_articles("Nature", 5)
#print(articles)

# API Documentation
# https://developers.openai.com/api/reference/overview
# https://ai.google.dev/gemini-api/docs#rest

# Websocket vs Requests (HTTP) vs library ?

# Using REST:

# The request format is the same between all APIs: a URL, headers, and JSON data.
# The differences are slight in formatting and structure of the request and response.
class ChatbotAPI:
    api_url = None
    request_json = None
    request_headers = None
    models = []

    # Do specific API formatting stuff in children...
    @classmethod
    def set_model(cls, model): pass
    @classmethod
    def set_prompt(cls, prompt): pass
    @staticmethod
    def parse_response(prompt_response): pass

    # Get a JSON response to prompt 
    @classmethod
    def send_prompt(cls, model, prompt):
        cls.set_model(model)
        cls.set_prompt(prompt)
        return requests.post(cls.api_url, headers=cls.request_headers, json=cls.request_json)


# !!! OPEN_AI is not free :( so this is kinda useless
class OpenAI(ChatbotAPI):
    api_url = "https://api.openai.com/v1/responses"
    request_json = {"model": None, "input": None}
    request_headers = {"Authorization": f"Bearer {KEYS['OPENAI']}",
                       "Content-Type": "application/json"}
    models = ["gpt-5"] # Fill later, or request from API in a constructor.

    @classmethod
    def set_model(cls, model): cls.request_json["model"] = model
    @classmethod
    def set_prompt(cls, prompt): cls.request_json["input"] = prompt
    @staticmethod
    def parse_response(response):
        try: return response.json()["output"]["content"][0]["text"]
        except Exception as e:
            print("\n ! Something went wrong ! \n\n ", e, "\n\n", response.text)
            return None

class Gemini(ChatbotAPI):
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/_:generateContent"
    request_json = {"contents": {"parts": {"text": None}}}
    request_headers = {"x-goog-api-key": KEYS['GEMINI'],
                       "Content-Type": "application/json"}
    models = ["gemini-3.5-flash"] # Fill later, or request from API in a constructor.

    @classmethod               # Gemini puts the model in the URL, not the JSON
    def set_model(cls, model): cls.api_url = cls.api_url[0:56]+model+":generateContent"
    @classmethod
    def set_prompt(cls, prompt): cls.request_json["contents"]["parts"]["text"] = prompt
    @staticmethod
    def parse_response(response):
        try: return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print("\n ! Something went wrong ! \n\n ", e, "\n\n", response.text)
            return None

# Prompting:

#response = OpenAI.send_prompt("gpt-5", input("Enter your GPT-5 prompt: "))
#print("\nThe response is: \n\n", OpenAI.parse_response(response))
#()

#response = Gemini.send_prompt("gemini-2.5-flash", input("Enter your Gemini-2.5-flash prompt: "))
#print("\nThe response is: \n\n", Gemini.parse_response(response))
#print()
