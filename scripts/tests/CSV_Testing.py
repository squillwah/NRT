import csv
import openpyxl
import json

def write_csv(inputted_json):

    with open(inputted_json, 'r', encoding='utf-8') as file:
        data = json.load(file)

    json_results = data["results"]
    json_keynames = data["components"]
    journal_id = str(data["id"])

    json_keynames.insert(0, "model")
    json_keynames.remove("REFERENCE")
    json_keynames.remove("url_abstract")
    json_keynames.remove("url_direct")
    json_keynames.insert(1, "REFERENCE")


    with open(journal_id + ".csv", "w") as csv_f:
        writer = csv.writer(csv_f)

        writer.writerow(json_keynames)

        for model in json_results:
            model_results = json_results[model]
            for form in model_results:
                if model_results[form] is not None:
                    component_data = model_results[form]
                    csv_f.write(model + ",")
                else:
                    continue
                for component in component_data:
                    csv_f.write(str(component_data[component]["validity"]))
                    csv_f.write(",")
                csv_f.write("\n")


def write_all_csv(inputted_json):
    with open(inputted_json, 'r', encoding='utf-8') as file:
        data = json.load(file)

        for paper in data:
            write_csv(data[paper])

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


test_data = [
    [{"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Chat-GPT"},
    {"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Gemini"}],
    [{"Overall": "Real", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Chat-GPT"},
    {"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Gemini"}]
]

pmids = ["65sd4f3654f", "4d441dsf44"]

if __name__ == "__main__":
    write_csv("1.json")

