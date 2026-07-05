
import json
from copy import deepcopy

# brealdowm
#  restircit refs to articles only X
#  create refdata format  X
#  pull apart ris into that X
#  store puzzlepiece set X
# All reference formats use the abreviation, is storing the full needed? It could be useful for adding error. !! Have a "minor quirks" subset, where the reference is real but some of the formatting is off.

# Definitive and formal list of all the unique components we're considering.
COMPONENT_LIST = ("authors", "title", "journal_name", "journal_volume", "journal_issue", "journal_page",
                  "elocator", "publication_date", "doi", "url_abstract", "url_direct", "pmcid", "pmid")
                  # *notes
                  #   no distinction is made (pairs always modified in same step) between:
                  #     short and full journal names
                  #     start and end journal pages
                  #     pub date and epub date
                  #   we're making a big deal out of PMID and PMCID cause our data source is PubMed, but know the majority of IRL refs have neither.

def make_ref():
    return {
        "authors": [],
        "title": "",
        "journal": {
            "name": { "full": "", "short": "" },
            "volume": None,
            "issue": None,
            "page": { "start": "", "end": "" },
            "elocator": "",
        },
        "pub": { "y": None, "m": None, "d": None },   # Date published (in journal)
        "epub": { "y": None, "m": None, "d": None },  # Date published (digitally)
        "doi": { "prefix": "", "suffix": "" },
        "url_abstract": "",
        "url_direct": "",
        "pmcid": "",
        "pmid": ""
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
            case "VL": refdata["journal"]["volume"] = int(value)
            case "IS": refdata["journal"]["issue"] = int(value)
            case "SP":              # RIS from PMC occasionally uses SP/EP to denote eLocators and DOIs
                if value.isdigit(): refdata["journal"]["page"]["start"] = int(value)
                elif value[0] == "e" and value[1:].isdigit(): refdata["journal"]["elocator"] = value
                else: print(f" ! [ristoref] bad SP (doi?): {value}")
            case "EP":
                if value.isdigit(): refdata["journal"]["page"]["end"] = int(value)
                elif value[0] == "e" and value[1:].isdigit(): refdata["journal"]["elocator"] = value
                else: print(f" ! [ristoref] bad EP (doi?): {value}")
            case "Y1": refdata["pub"]["y"], refdata["pub"]["m"], refdata["pub"]["d"] = (x := [int(n) for n in value.split("/") if n.isdigit()]) + [None]*(3-len(x)) # Publication dates are not always complete.
            case "ET": refdata["epub"]["y"], refdata["epub"]["m"], refdata["epub"]["d"] = (x := [int(n) for n in value.split("/") if n.isdigit()]) + [None]*(3-len(x))
            case "DO": refdata["doi"]["prefix"], refdata["doi"]["suffix"] = value.split("/")
            case "UR": refdata["url_abstract"] = value
            case "L2": refdata["url_direct"] = value
            case "U2": refdata["pmcid"] = value[:-7] # Slice off trailing ...[pmcid]
            case "AN": refdata["pmid"] = value
            #case _: print(f"! unknown RIS tag: {(tag, value)}")
    return refdata

# Create flat reference component set from multiple reference datas
def component_set(*refdata):
    compset = make_ref()
    for key in compset:
        compset[key] = []
        for ref in refdata:
            compset[key].append(deepcopy(ref[key]))

    # Additional sets for picking differents accross many duplicates
    #compset["jname_set"] = { "full": list({fn for fn in [j["name"]["full"] for j in compset["journal"]]}),
    #                         "short": list({sn for sn in [j["name"]["short"] for j in compset["journal"]]}) }
    compset["sets"] = {
        "journal_name": [dict(zip(("full", "short"), jname)) for jname in {tuple(j["name"].values()) for j in compset["journal"]}], # A set of every journal name (short/full dicts)
        "journal_elocator": list({j["elocator"] for j in compset["journal"]}),
        "doi_prefix": list({doi["prefix"] for doi in compset["doi"]}),
        "doi_suffix": list({doi["suffix"] for doi in compset["doi"]})   # The brackets are set notation, btw. (and list cause sets are jsonable)
    }
    print(compset["sets"]["journal_name"])
    return compset

# Tests
if __name__ == "__main__":
    FILE = "./reference_ris.json"

    refs = None
    with open(FILE, "r") as file:
        refs = json.load(file)

    #refdata = [ristoref(r["ris"]) for r in refs]
    refdata = [ristoref(r) for r in refs]
    compset = component_set(*refdata)

    # Checking, all should be 100
    print(json.dumps(refdata, indent=2))
    #print(json.dumps(compset, indent=4))
    for key in compset:
        print(key, len(compset[key]))
        if isinstance(compset[key], dict):
            for subkey in compset[key]:
                print("-", subkey, len(compset[key][subkey]))
#    for r in refs:
#        print("-"*20)
#        print(r)

