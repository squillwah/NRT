
from pathlib import Path
from tools.references.refdata import ReferenceComponent
import json
import tools.help as h
import csv
log = h.log

#@TODO Add threading to evaluator script

if __name__ == "__main__":
    path_dataset = Path("./mme/source.json")
    path_results = Path("./mme/results/all.json")
    #dataset, results = None, None
    #with open(path_dataset, "r") as f: dataset = json.load(f)
    #with open(path_results, "r") as f: results = json.load(f)
    dataset = h.read_json(path_dataset, intkeys=True)
    results = h.read_json(path_results, intkeys=True)
    #print(json.dumps(results, indent=2))

    #for x in (dataset[0], results[0]):
    #    print(json.dumps(x, indent=2))


    # Layout
    # ,             accuracy_component1, confidence_component1, accuracy_component2, confidence_component2, ...
    # model1_format,
    # model2_format,
    # ...

    # 1 or 2 files? Accuracy and confidence together or seperate?
    # Seperate.

    # A third for reasoning? Or just keep as json...
  
    #columns_a = [header for comp in ReferenceComponent for header in (f"{comp}_a", f"{comp}_c")]

    lens = (len(dataset), len(results))
    log("Dataset Size:", lens[0])
    log("Results Size:", lens[1])
    if lens[0] != lens[1]: log("Sizes are different, are you sure source and results align?", t="? ")
    log("Iterating results, grading model responses against dataset scores.")
    
    #COLUMNS = [""] + [str(c) for c in ReferenceComponent] + ["REFERENCE"]
    
    for ID in results:
        log("ID:", ID)
       
        headers = results[ID]["components"]
        headers.remove("url_abstract")          # @TODO Fix the issue behind this workaround.
        headers.remove("url_direct")

        rows = {
            "accuracy": [["model", "format"]+headers],
            "confidence": [["model", "format"]+headers]
        }

        for model in results[ID]["results"]:
            for form in results[ID]["results"][model]:
                if not results[ID]["results"][model][form]: continue # Entries for untested formats still exist, but with null values.

                for datum_type in rows:
                    row = [model, form]
                    
                    for c in headers: 
                        response = results[ID]["results"][model][form]["response"]
                        if not isinstance(response, dict):
                            log("BAD response format", model, form, c, t="e")
                            continue
                        
                        datum = None 
                        if datum_type == "accuracy": 
                            datum = response[c]["validity"]  
                            truth = None
                            if (c == "REFERENCE"): # @JANK silly workaround for the added holistic "REFERENCE" component (which is under holistic_complete in ds scores)
                                truth = dataset[ID]["scores"]["holistic_complete"][0]   # @TODO !!! Still need to calculate the 'holistic_formatted' scores in the DS!
                            elif dataset[ID]["scores"]["component"][c] is not None: 
                                truth = dataset[ID]["scores"]["component"][c][0]
                            datum = (datum == truth) if truth is not None else f"{datum}(null)" # Compare model answer with truth if truth exists, set NULL_<answer> if truth nonexistent.
                        elif datum_type == "confidence":
                            datum = response[c]["validity_confidence"]  
                        else: log("UHOH!", t="e")

                        row.append(datum)

                    rows[datum_type].append(row)
                
        log(f"Writing accuracy and confidence CSVs for ID {ID}")

        for datum_type in rows:
            with open(f"{ID}_{datum_type}.csv", mode="w", newline='') as f:
                writer = csv.writer(f) 
                writer.writerows(rows[datum_type])


        for t in rows:
            for r in rows[t]: print(r)

        #log("
                    

# @TODO a better layout

# model, format, component_m (MODEL), component_T (TRUTH)   
#                   true                  true
#                   true                  null  < If component not present in (SPECIFIC REFERENCE FORMAT, not entire reference data)
#                   false                 true

        
