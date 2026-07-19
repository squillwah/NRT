
import csv
import glob
import re
import numpy as np

class datum:
    def __init__(self):
        self.total = 0
        self.count = 0
    def add(self, value):
        self.total += value
        self.count += 1
    def average(self):
        return self.total/self.count

def model_matrices(files, value_operation):
    matrices = {}
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                model, _, values = row[0], row[1], [value_operation(v) for v in row[2:]] # Slice model style heads
                if model not in matrices: matrices[model] = []
                matrices[model].append(values)
    return matrices

def average_rows(matrix):
    sums = [datum() for i in matrix[0]] # Rows should be of equal length
    for row in matrix:
        for i, value in enumerate(row):
            if value is not None:       # Accuracy values are NULL if the component was not in the reference.
                sums[i].add(value)
    return [s.average() for s in sums]

def to_csv(filename, averages):
    HEADER = ("model","REFERENCE","authors","title","journal_name","journal_volume","journal_issue","journal_page","elocator","publication_date","doi","pmcid","pmid")  # 'Style' is removed.
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows([[model]+average for model, average in averages.items()])


files_accuracy_all = glob.glob("./csvs/*_accuracy.csv")
files_confidence_all = glob.glob("./csvs/*_confidence.csv")

files_accuracy_source, files_accuracy_mutated = [], []
files_confidence_source, files_confidence_mutated = [], []

for file in files_accuracy_all:
    match = re.search(r'\d+', file)
    if match:
        num = int(match.group(0))
        if num < 120:
            files_accuracy_source.append(file)
        else:
            files_accuracy_mutated.append(file)

for file in files_confidence_all:
    match = re.search(r'\d+', file)
    if match:
        num = int(match.group(0))
        if num < 120:
            files_confidence_source.append(file)
        else:
            files_confidence_mutated.append(file)

# { <model>: [] }
all_accuracy_all = model_matrices(files_accuracy_all, lambda v: int(v.lower() == "true") if v != "" else None)
all_accuracy_source = model_matrices(files_accuracy_source, lambda v: int(v.lower() == "true") if v != "" else None)
all_accuracy_mutated = model_matrices(files_accuracy_mutated, lambda v: int(v.lower() == "true") if v != "" else None)
all_confidence_all = model_matrices(files_confidence_all, lambda v: float(v))
all_confidence_source = model_matrices(files_confidence_source, lambda v: float(v))
all_confidence_mutated = model_matrices(files_confidence_mutated, lambda v: float(v))

# { <model>: [] }
avg_accuracy_all = {}
avg_accuracy_source = {}
avg_accuracy_mutated = {}
for model, matrix in all_accuracy_all.items():
    avg_accuracy_all[model] = average_rows(matrix)
for model, matrix in all_accuracy_source.items():
    avg_accuracy_source[model] = average_rows(matrix)
for model, matrix in all_accuracy_mutated.items():
    avg_accuracy_mutated[model] = average_rows(matrix)
avg_confidence_all = {}
avg_confidence_source = {}
avg_confidence_mutated = {}
for model, matrix in all_confidence_all.items():
    avg_confidence_all[model] = average_rows(matrix)
for model, matrix in all_confidence_source.items():
    avg_confidence_source[model] = average_rows(matrix)
for model, matrix in all_confidence_mutated.items():
    avg_confidence_mutated[model] = average_rows(matrix)

to_csv("./avg_accuracy_all.csv", avg_accuracy_all)
to_csv("./avg_accuracy_source.csv", avg_accuracy_source)
to_csv("./avg_accuracy_mutated.csv", avg_accuracy_mutated)
to_csv("./avg_confidence_all.csv", avg_confidence_all)
to_csv("./avg_confidence_source.csv", avg_confidence_source)
to_csv("./avg_confidence_mutated.csv", avg_confidence_mutated)


