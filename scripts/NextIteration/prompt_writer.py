
# Prompt pieces:

use_internet = "You may use the internet. "
dont_use_internet = "DO NOT USE INTERNET. "
internet_query = "Did you use the internet? "

general_prompt = "Analyze this citation and tell me if its real or not. In the response use the words \"not real\" if the citation is in not real, and use the words \" is real\" if the citation is real."

percentage_confidence = "What percentage confidence do you think this citation is real? Then explain how you came up with that number. "
accuracy_prompt_simple = "Is this citation accurate? Yes or No "

explanation = "Please explain every decision you make."


def generate_prompt():
    prompt = ""
    prompt += general_prompt
    if input("Do you want to let the model use the internet? y/n\n") == "y":
        prompt += use_internet
    else:
        prompt += dont_use_internet
    if input("Do you want the percentage of confidence? y/n\n") == "y":
        prompt += percentage_confidence
    if input("Do you want the accuracy? y/n\n") == "y":
        prompt += accuracy_prompt_simple

    prompt += internet_query
    prompt +=  explanation

    return prompt