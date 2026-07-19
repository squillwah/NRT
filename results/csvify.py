


import csv
import json
from pathlib import Path

READ = Path("./out")
WRITE = Path("./csvs")

for f_json in READ.iterdir():
    if f_json.is_file():
        with open(f_json, 'r') as f1, open(WRITE / f"{f_json.stem}.csv", mode='w', newline='', encoding='utf-8') as f2:
            results = json.load(f1)
            writer = csv.writer(f2)
            
            writer.writerow(list(results[0].keys()))
            writer.writerows([list(result.values()) for result in results])

