
import json
from copy import deepcopy

# brealdowm
#  restircit refs to articles only X
#  create refdata format  X
#  pull apart ris into that X
#  store puzzlepiece set X
# All reference formats use the abreviation, is storing the full needed? It could be useful for adding error. !! Have a "minor quirks" subset, where the reference is real but some of the formatting is off.

def make_ref():
    return {
        "authors": [],  # @todo: split author names into first and last
        "title": "",
        "journal": {
            "name": { "full": "", "short": "" },
            "volume": "",
            "issue": "",
            "page": { "start": "", "end": "" }
        },
        "pub": { "y": "", "m": "", "d": "" },   # Date published (in journal)
        "epub": { "y": "", "m": "", "d": "" },  # Date published (digitally)
        "doi": "",
        "pmid": "",
        "pmcid": ""
    }

# Parse RIS into dictionary representation
# https://en.wikipedia.org/wiki/RIS_(file_format)
def ristoref(ris):
    refdata = make_ref()
    risitems = [(line[0:2], line[6:]) for line in ris.split("\r\n") if len(line) != 0] # Split leaves a trailing '', could slice final index instead of condition.
    for tag, value in risitems:
        match tag:
            #case "AU": refdata["authors"].append(value)
            case "AU": refdata["authors"].append(dict(zip(["l", "f"], (names := value.split(", "))+[""]*(2-len(names))))) # Split authors into dicts of {'l': "last", 'f': "first"} 
            case "T1": refdata["title"] = value
            case "JF": refdata["journal"]["name"]["full"] = value
            case "J2": refdata["journal"]["name"]["short"] = value
            case "VL": refdata["journal"]["volume"] = value
            case "IS": refdata["journal"]["issue"] = value
            case "SP": refdata["journal"]["page"]["start"] = value
            case "EP": refdata["journal"]["page"]["end"] = value
            case "Y1": refdata["pub"]["y"], refdata["pub"]["m"], refdata["pub"]["d"] = (x := value.split("/")) + [""]*(3-len(x)) # Publication date is not always precise.
            case "ET": refdata["epub"]["y"], refdata["epub"]["m"], refdata["epub"]["d"] = value.split("/")
            case "DO": refdata["doi"] = value
            case "AN": refdata["pmid"] = value
            case "U2": refdata["pmcid"] = value[:-7] # Slice off trailing ...[pmcid]
            #case _: print(f"! unknown RIS tag: {(tag, value)}")
    return refdata

# Create flat reference component set from multiple reference datas
def component_set(*refdata):
    compset = make_ref()
    for key in compset:
        compset[key] = []
        for ref in refdata:
            compset[key].append(deepcopy(ref[key]))
    return compset

# Tests
if __name__ == "__main__":
    FILE = "./references.json"

    refs = None
    with open(FILE, "r") as file:
        refs = json.load(file)

    refdata = [ristoref(r["ris"]) for r in refs]
    compset = component_set(*refdata)

    # Checking, all should be 100
    print(json.dumps(refdata, indent=4))
    print(json.dumps(compset, indent=4))
    for key in compset:
        print(len(compset[key]))

