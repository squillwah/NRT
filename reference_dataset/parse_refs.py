
import json

# brealdowm
#  restircit refs to articles only X
#  create refdata format  X
#  pull apart ris into that X
#  store puzzlepiece set X

_MONTHMAP = {"01": "Jan", "02": "Feb", "03": "Mar",
             "04": "Apr", "05": "May", "06": "Jun",
             "07": "Jul", "08": "Aug", "09": "Sep",
             "10": "Oct", "11": "Nov", "12": "Dec"}

# Parse RIS into dictionary representation
# https://en.wikipedia.org/wiki/RIS_(file_format)
def parse_ris(ris):
    refdata = {
        "authors": [],
        "title": "",    # All reference formats use the abreviation, is storing the full needed? It could be useful for adding error. !! Have a "minor quirks" subset, where the reference is real but some of the formatting is off.
        "journal": { "name": { "full": "", "short": "" }, "year": "", "volume": "", "issue": "":, "page": { "start": "", "end": "" }},
        "doi": "",
        "epub": { "y": "", "m": "", "d": "" }, # For NLM format. 
        "pmid": "",                                     #
        "pmcid": ""                                     #
    }
    for tag, value in [(line[0:2], line[6:]) for line in ris.split("\r\n") if len(line) != 0]: # Split leaves a trailing '', could slice final index instead of condition.
        match tag:
            case "AU": refdata["authors"].append(value)
            case "T1": refdata["title"] = value
            case "JF": refdata["journal"]["name"]["full"] = value
            case "J2": refdata["journal"]["name"]["short"] = value
            case "Y1": refdata["journal"]["year"] = value[0:4] # All formats only include publication year.
            case "VL": refdata["journal"]["volume"] = value
            case "SP": refdata["journal"]["page"] = value
            case "DO": refdata["doi"] = value
            case "ET": refdata["epub"]["y"], refdata["epub"]["m"], refdata["epub"]["d"] = value.split("/") # Only NLM includes epub.
            case "AN": refdata["pmid"] = value
            case "U2": refdata["pmcid"] = value[:-7] # Slice off trailing ...[pmcid]
            #case _: print(f"! unknown RIS tag: {(tag, value)}")
    return refdata

# Return reference component set from multiple reference data dicts
def component_set(*refdata):
    compset = {
        "authors": { "single": [], "groups": [] },
        "titles": [],
        "journals": { "names": { "full": [], "short": [] }, "years": [], "volumes": [], "pages": [] },
        "dois": [],
        "epubs": { "ys": [], "ms": [], "ds": [] },
        "pmids": [],
        "pmcids": []
    }
    for rd in refdata:
        compset["authors"]["single"].extend(rd["authors"])
        compset["authors"]["groups"].append(rd["authors"])
        compset["titles"].append(rd["title"])
        compset["journals"]["names"]["full"].append(rd["journal"]["name"]["full"])
        compset["journals"]["names"]["short"].append(rd["journal"]["name"]["short"])
        compset["journals"]["years"].append(rd["journal"]["year"])
        compset["journals"]["volumes"].append(rd["journal"]["volume"])
        compset["journals"]["pages"].append(rd["journal"]["page"])
        compset["dois"].append(rd["doi"])
        compset["epubs"]["ys"].append(rd["epub"]["y"])
        compset["epubs"]["ms"].append(rd["epub"]["m"])
        compset["epubs"]["ds"].append(rd["epub"]["d"])
        compset["pmids"].append(rd["pmid"])
        compset["pmcids"].append(rd["pmcid"])
    return compset

# Construct AMA reference string from refdata
def build_ama(data):
    formatted_authors = []
    for author in data["authors"]:
        if "," in author:
            last, first = author.split(",", 1)
            initials = "".join([i[0] for i in first.strip().split()])
            formatted_authors.append(f"{last.strip()} {initials}")
        else:
            formatted_authors.append(author)
    if len(formatted_authors) >= 7: # because ama really wants to get specific. 
        author_str = ", ".join(formatted_authors[:3]) + ", et al"
    else:
        author_str = ", ".join(formatted_authors)
    month_lbl = ""#get_month_abbr(data["month"])
    day_lbl = ""#data["day"].lstrip('0') if data["day"] else ""
    return f"{author_str}. {data['title']}. {data['journal']['name']['short']}. {data['journal']['year']};{data['journal']['volume']}:{data['journal']['page']}. Published {data['journal']['year']} {month_lbl} {day_lbl}. doi:{data['doi']}"



# Tests
if __name__ == "__main__":
    FILE = "./references.json"

    refs = None
    with open(FILE, "r") as file:
        refs = json.load(file)

    data = parse_ris(refs[0]["ris"])
    #print(data["authors"])

    #print(json.dumps(refs[0], indent=4))
    #print(json.dumps(data, indent=4))

    #formatted = [{ "id": ref["id"], "data": parse_ris(ref["ris"]) } for ref in refs]
    refdata = [parse_ris(ref["ris"]) for ref in refs]
    #print(json.dumps(formatted, indent=4))
    compset = component_set(*refdata)
    print(json.dumps(compset, indent=4))

    # Checking, all should be 100
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

    print()
    print(build_ama(refdata[0]))
    print()
    print(refs[0]["ama"]["orig"])




























# There is the choice between eight functions or two with some format specific argument.
# If the logic overlaps a lot, just two would be more concise.


# Takes reference string and returns some standard representation for versitile mangling.
# Compose does the reverse.

# Alternatively, we could try to use the RIS shit as our standard format, and just build each format from scratch with that.
# We would probably make some subtle mistakes and it'd be hard to match 100% with the real references completely. 

# Global patterns:
# - Authors always first.

# Which parts are irrecoverably different?
# - Et al vs full list
"""
def decompose_ama(ref):
    # Patterns of AMA:
    # - "Authors. Title. Journal. JournalYear;Volume:Page/Elocator. Published Year Mon Da. doi"
    # - All author names listed
    #   - last[full]+SPACE+first[initial]+(COMMA+SPACE+repeat)+PERIOD
    #   - no periods on initials, no spacing between multiple initials
    # 

    # The standard format should be a map something like:
    # {"authors": ["", "", ""], # What to do for et al? A single element list or break convention with a plain string?
    #   "title": "",
    #   "published": "", # Could be broken down further, into month day year
    #   "journal": "",   # Would there be a seperate journal date from publishing date?
    #   "volume": "",
    #   "page": "",
    #   "doi": ""}
    # The tricky part is deciding on a structure which works for all formats, so we don't need to write multiple procedures for each one permutation.

    # Could we use RegEx?

def compose_ama(ref): pass
    # The reverse of decompose

def decompose_apa(ref): pass
def compose_apa(ref): pass

def decompose_mla(ref): pass
def compose_mla(ref): pass

def decompose_nlm(ref): pass
def compose_nlm(ref): pass


#jref = decompose_ama(the_string)
ref = decompose_apa(the_string)

def swap_authors(ref):
    swap(ref["authors"])
    return ref

apa = compose_apa(ref)

def mangle_title(ref, settings):
    for i in range(times):
        introduce_typo(ref["title"], random_point, random_type)
main():
    # 200 single
    for i in 200:
        random_mutation(ref)
    # 300 multi
"""
