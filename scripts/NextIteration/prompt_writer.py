from datetime import datetime
# Prompt pieces:

use_internet = "You may use the internet. "
dont_use_internet = "DO NOT USE INTERNET. "

general_prompt = "Analyze this citation and tell me whether its real or not."

percentage_confidence = "What percentage confidence do you think this citation is real or not?"

# Getting current date and time

current_datetime = datetime.now()

formatted_datetime = current_datetime.strftime("%m/%d/%Y, %H:%M:%S")


def generate_prompt():
    prompt = ""
    prompt += general_prompt + "Current date and time: " + formatted_datetime
    if input("Do you want to let the model use the internet? y/n\n") == "y":
        prompt += use_internet
    else:
        prompt += dont_use_internet

    return prompt