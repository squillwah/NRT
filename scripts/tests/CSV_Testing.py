import csv
import openpyxl
from openpyxl import Workbook
import json

def write_csv(inputted_json):

    with open(inputted_json, 'r', encoding='utf-8') as file:
        data = json.load(file)


    with open("output.csv", "w", newline="") as csv_f:
        headers = data[0].keys()

        writer = csv.DictWriter(csv_f,fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


    #----Another possible method using a library (found as an example)----
    # import pandas as pd
    #
    # # Load the JSON file directly into a DataFrame
    # df = pd.read_json("data.json")
    #
    # # Export to a CSV file (index=False prevents writing row numbers)
    # df.to_csv("output.csv", index=False)



def write_xlsx(inputted_data, pmid_list):

    wb = openpyxl.Workbook()

    # Remove the default sheet created by openpyxl so it doesn't leave an empty sheet
    default_sheet = wb.active
    wb.remove(default_sheet)

    # 2. Iterate through the list of dictionaries
    for i, dict_list in enumerate(inputted_data):

        ws = wb.create_sheet(title=pmid_list[i])

        headers = list(dict_list[0].keys())
        ws.append(headers)
        for inputted_dict in dict_list:

            # Extract headers and values for THIS dictionary specifically

            values = [inputted_dict[key] for key in headers]

            # Append the headers as row 1, and values as row 2

            ws.append(values)

    wb.save(filename="output.xlsx")


data = [
    [{"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Chat-GPT"},
    {"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Gemini"}],
    [{"Overall": "Real", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Chat-GPT"},
    {"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Gemini"}]
]

pmids = ["65sd4f3654f", "4d441dsf44"]

if __name__ == "__main__":
    write_xlsx(data, pmids)

