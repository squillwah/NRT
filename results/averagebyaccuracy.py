import glob
import csv
import numpy as np

# Return dict of CSV values
# {model: {refID: [v1, v2, ...], ...}, ...} (style tag is not kept)
def parse_csvs(filenames):
    parsed = {}
    for filename in filenames:
        with open(filename, 'r', encoding="utf-8") as file:
            ref, reader = int(filename.split("/")[-1].split("_")[0]), csv.DictReader(file)
            # add model
            for row in reader:
                row = list(row.values()) # Assuming order is always CSV column order...
                model, style, confs = row[0], row[1], row[2:]
                if model not in parsed: parsed[model] = {}
                parsed[model][ref] = confs
    return parsed

files_accuracy_all = glob.glob("./csvs/*_accuracy.csv")
files_confidence_all = glob.glob("./csvs/*_confidence.csv")
accuracy_data, confidence_data = parse_csvs(files_accuracy_all), parse_csvs(files_confidence_all)

models = list(confidence_data.keys())
right_confs, wrong_confs, rc_avg, wc_avg = [{model: {} for model in models} for _ in range(4)]

for model, references in confidence_data.items():
    for refID, confidences in references.items():
        score = accuracy_data[model][refID][0].lower() == "true"
        confs = right_confs if score else wrong_confs
        confs[model][refID] = confidences

matrix = lambda lists: np.array([[float(i) for i in l] for l in lists])
for model in models:
    rc_avg[model] = np.mean(matrix(right_confs[model].values()), axis=0)
    wc_avg[model] = np.mean(matrix(wrong_confs[model].values()), axis=0)

print(rc_avg)
print(wc_avg)
print("RIGHT\n", {model: data[0] for model, data in rc_avg.items()})
print("WRONG\n", {model: data[0] for model, data in wc_avg.items()})

