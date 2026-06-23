import csv
import openpyxl
from openpyxl import Workbook

def write_csv(inputted_dict):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Output from Models"

    for i in range(len(inputted_dict)):
        new_sheet = wb.create_sheet(title="Test" + str(i))
        headers = ["Overall", "Author", "Journal", "Publish Date", "Author Order", "Publisher", "Percentage of Confidence", "Model"]

        new_sheet.append(headers)
        for item in inputted_dict:
            row_values = [item[key] for key in headers]
            new_sheet.append(row_values)

    wb.save(filename="output.xlsx")




# data = [
#     {"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Chat-GPT"},
#     {"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Gemini"}
# ]
#
# wb = openpyxl.Workbook()
# ws = wb.active
# ws.title = "Test 1"
#
# for i in range(len(data)):
#     new_sheet = wb.create_sheet(title="Test" + str(i))
#     headers = ["Overall", "Author", "Journal", "Publish Date", "Author Order", "Publisher", "Percentage of Confidence", "Model"]
#
#     new_sheet.append(headers)
#     for item in data:
#         row_values = [item[key] for key in headers]
#         new_sheet.append(row_values)
#
#
# wb.save(filename= "output.xlsx")

# make a final column of what the correct answer should be
# need to create a full excel

