import glob
import csv
import numpy as np
import matplotlib.pyplot as plt

# Return dict of CSV values
# {model: {refID: [v1, v2, ...], ...}, ...} (style tag is not kept)
def parse_csvs(filenames, element_operation=None):
    parsed = {}
    for filename in filenames:
        with open(filename, 'r', encoding="utf-8") as file:
            ref, reader = int(filename.split("/")[-1].split("_")[0]), csv.DictReader(file)
            # add model
            for row in reader:
                row = list(row.values()) # Assuming order is always CSV column order...
                model, style, values = row[0], row[1], row[2:]
                if model not in parsed: parsed[model] = {}
                parsed[model][ref] = [element_operation(v) for v in values] if element_operation is not None else values
    return parsed

files_accuracy_all = glob.glob("./csvs/*_accuracy.csv")
files_confidence_all = glob.glob("./csvs/*_confidence.csv")
accuracy_data = parse_csvs(files_accuracy_all, lambda v: bool(v.lower() == "true"))
confidence_data = parse_csvs(files_confidence_all, lambda v: float(v))

models = list(confidence_data.keys())
right_confs, wrong_confs, rc_avg, wc_avg = [{model: {} for model in models} for _ in range(4)]

for model, references in confidence_data.items():
    for refID, confidences in references.items():
        #score = accuracy_data[model][refID][0].lower() == "true"
        score = accuracy_data[model][refID][0]  # Holistic score.
        confs = right_confs if score else wrong_confs
        confs[model][refID] = confidences

#matrix = lambda lists: np.array([[float(i) for i in l] for l in lists])
for model in models:
    rc_avg[model] = np.mean(list(right_confs[model].values()), axis=0)
    wc_avg[model] = np.mean(list(wrong_confs[model].values()), axis=0)

print(rc_avg)
print(wc_avg)
print("RIGHT\n", {model: data[0] for model, data in rc_avg.items()})
print("WRONG\n", {model: data[0] for model, data in wc_avg.items()})

x, y = [], []
for model, model_accuracies in accuracy_data.items():
    for refID, component_accuracies in model_accuracies.items():
        x.append(refID)
        y.append(sum(int(component_accuracy) for component_accuracy in component_accuracies))
        #y.append(component_accuracies[0])

plt.scatter(x, y, s=1)
plt.show()
