
import json

# brealdowm
#  restircit refs to articles only X
#  create refdata format  X
#  pull apart ris into that X
#  store puzzlepiece set X

# Parse RIS into dictionary representation
# https://en.wikipedia.org/wiki/RIS_(file_format)
def parse_ris(ris):
    refdata = {
        "authors": [],
        "title": "",
        "journal": {
            "name_full": "", # All reference formats use the abreviation, is storing the full needed? It could be useful for adding error. !! Have a "minor quirks" subset, where the reference is real but some of the formatting is off.
            "name_short": "",
            "volume": "",
            "issue": "",
            "page_start": "",
            "page_end": ""
        },
        "pub": { "y": "", "m": "", "d": "" },   # Date published (in journal)
        "epub": { "y": "", "m": "", "d": "" },  # Date published (digitally)
        "doi": "",
        "pmid": "",
        "pmcid": ""
    }
    for tag, value in [(line[0:2], line[6:]) for line in ris.split("\r\n") if len(line) != 0]: # Split leaves a trailing '', could slice final index instead of condition.
        match tag:
            case "AU": refdata["authors"].append(value)
            case "T1": refdata["title"] = value
            case "JF": refdata["journal"]["name_full"] = value
            case "J2": refdata["journal"]["name_short"] = value
            case "VL": refdata["journal"]["volume"] = value
            case "IS": refdata["journal"]["issue"] = value
            case "SP": refdata["journal"]["page_start"] = value
            case "EP": refdata["journal"]["page_end"] = value
            case "Y1": refdata["pub"]["y"], refdata["pub"]["m"], refdata["pub"]["d"] = (x := value.split("/")) + [""]*(3-len(x)) # Publication date is not always precise.
            case "ET": refdata["epub"]["y"], refdata["epub"]["m"], refdata["epub"]["d"] = value.split("/")
            case "DO": refdata["doi"] = value
            case "AN": refdata["pmid"] = value
            case "U2": refdata["pmcid"] = value[:-7] # Slice off trailing ...[pmcid]
            #case _: print(f"! unknown RIS tag: {(tag, value)}")
    return refdata

# Create flat reference component set from multiple reference datas
def component_set(*refdata):
    # Could have the structure mirror 1-1 (of course with lists instead of single strings), would be easier to expand that way.
    compset = {
        "authors": { "single": [], "groups": [] },
        "titles": [],
        "journals": { "names": { "full": [], "short": [] }, "years": [], "volumes": [], "issues": [], "pages": [] },
        "dois": [],
        "epubs": { "ys": [], "ms": [], "ds": [] },
        "pmids": [],
        "pmcids": []
    }
    for rd in refdata:
        compset["authors"]["single"].extend(rd["authors"].copy())   # Make sure to copy the objs.
        compset["authors"]["groups"].append(rd["authors"].copy())
        compset["titles"].append(rd["title"])
        compset["journals"]["names"]["full"].append(rd["journal"]["name"]["full"])
        compset["journals"]["names"]["short"].append(rd["journal"]["name"]["short"])
        compset["journals"]["years"].append(rd["journal"]["year"])
        compset["journals"]["volumes"].append(rd["journal"]["volume"])
        compset["journals"]["pages"].append(rd["journal"]["pages"])
        compset["dois"].append(rd["doi"])
        compset["epubs"]["ys"].append(rd["epub"]["y"])
        compset["epubs"]["ms"].append(rd["epub"]["m"])
        compset["epubs"]["ds"].append(rd["epub"]["d"])
        compset["pmids"].append(rd["pmid"])
        compset["pmcids"].append(rd["pmcid"])
    return compset

# Tests
if __name__ == "__main__":
    FILE = "./references.json"

    refs = None
    with open(FILE, "r") as file:
        refs = json.load(file)

    refdata = [parse_ris(ref["ris"]) for ref in refs]
    compset = component_set(*refdata)

    # Checking, all should be 100
    print(json.dumps(compset, indent=4))
    #print(len(compset["authors"]["single"]))
    print(len(compset["authors"]["groups"]))
    print(len(compset["titles"]))
    print(len(compset["journals"]["names"]["full"]))
    print(len(compset["journals"]["names"]["short"]))
    print(len(compset["journals"]["years"]))
    print(len(compset["journals"]["volumes"]))
    print(len(compset["journals"]["pages"]))
    print(len(compset["dois"]))
    print(len(compset["epubs"]["ys"]))
    print(len(compset["epubs"]["ms"]))
    print(len(compset["epubs"]["ds"]))
    print(len(compset["pmids"]))
    print(len(compset["pmcids"]))

