import csv
import openpyxl
import json
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# def write_csv(inputted_json):
#
#     with open(inputted_json, 'r', encoding='utf-8') as file:
#         data = json.load(file)
#
#     json_results = data["results"]
#     json_keynames = data["components"]
#     journal_id = str(data["id"])
#
#     json_keynames.insert(0, "model")
#     json_keynames.remove("REFERENCE")
#     json_keynames.remove("url_abstract")
#     json_keynames.remove("url_direct")
#     json_keynames.insert(1, "REFERENCE")
#
#
#     with open(journal_id + ".csv", "w") as csv_f:
#         writer = csv.writer(csv_f)
#
#         writer.writerow(json_keynames)
#
#         for model in json_results:
#             model_results = json_results[model]
#             for form in model_results:
#                 if model_results[form] is not None:
#                     component_data = model_results[form]
#                     csv_f.write(model + ",")
#                 else:
#                     continue
#                 for component in component_data:
#                     csv_f.write(str(component_data[component]["validity"]))
#                     csv_f.write(",")
#                 csv_f.write("\n")


def write_all_csv(inputted_json):
    with open(inputted_json, 'r', encoding='utf-8') as file:
        data = json.load(file)

        for paper in data.values():

            json_results = paper["results"]
            json_keynames = paper["components"]
            journal_id = str(paper["id"])

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

def write_xlsx(inputted_csv):

    wb = openpyxl.Workbook()

    # Remove the default sheet created by openpyxl so it doesn't leave an empty sheet
    default_sheet = wb.active
    wb.remove(default_sheet)

    with open(inputted_csv, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        csv_id = str(inputted_csv.replace('.csv', ''))
        csv_lines = [row for row in reader]

        csv_lines.remove(csv_lines[1])

        xlsx_header = csv_lines[0]

        ws = wb.create_sheet(title=csv_id)

        ws.append(xlsx_header)

        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")  # Dark Blue
        header_align = Alignment(horizontal="center", vertical="center")

        # 4. Apply styling to row 1, freeze panes, and enable print titles
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align

        for row in csv_lines[1:]:
            ws.append(row)


        for col in ws.columns:
            max_len = 0
            column = col[0].column
            for cell in col:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))

            # Set width with buffer, min width 10
            adjusted_width = (max_len + 3)
            ws.column_dimensions[get_column_letter(column)].width = adjusted_width

        wb.save(filename=csv_id + ".xlsx")



    # # 2. Iterate through the list of dictionaries
    # for i, dict_list in enumerate(inputted_data):
    #
    #     ws = wb.create_sheet(title=pmid_list[i])
    #
    #     headers = list(dict_list[0].keys())
    #     ws.append(headers)
    #     for inputted_dict in dict_list:
    #
    #         # Extract headers and values for THIS dictionary specifically
    #
    #         values = [inputted_dict[key] for key in headers]
    #
    #         # Append the headers as row 1, and values as row 2
    #
    #         ws.append(values)
    #
    # wb.save(filename="output.xlsx")


test_data = [
    [{"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Chat-GPT"},
    {"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Gemini"}],
    [{"Overall": "Real", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Chat-GPT"},
    {"Overall": "Fake", "Author": "Real", "Journal": "Real", "Publish Date": "Fake", "Author Order": "Real", "Publisher": "Real", "Percentage of Confidence": 95.00001, "Model": "Gemini"}]
]

pmids = ["65sd4f3654f", "4d441dsf44"]

if __name__ == "__main__":
    write_xlsx('1.csv')
    # write_all_csv("all.json")
