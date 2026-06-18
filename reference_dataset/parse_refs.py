
import json

# brealdowm
#  restircit refs to articles only X
#  create refdata format 
#  pull apart ris into that
#  store puzzlepiece set

# Parse RIS into dictionary representation
# https://en.wikipedia.org/wiki/RIS_(file_format)
def parse_ris(ris):
    refdata = {
        "authors": [],
        "title": "",
        "journal": { "name": {"full": "", "short": ""}, "year": "", "volume": "", "page": "" },
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

        #if tag == "AU":
        #    ris_data["authors"].append(value)
        #elif tag == "T1":
        #    ris_data["title"] = value.rstrip(".")
        #elif tag == "Y1":
        #    date_parts = value.split('/')
        #    if len(date_parts) >= 1: ris_data["year"] = date_parts[0]
        #    if len(date_parts) >= 2: ris_data["month"] = date_parts[1]
        #    if len(date_parts) >= 3: ris_data["day"] = date_parts[2]
        #elif tag == "DO":
        #    ris_data["doi"] = value
        #elif tag == "VL":
        #    ris_data["volume"] = value
        #elif tag == "SP":
        #    ris_data["pages"] = value
        #elif tag == "J2":
        #    ris_data["journal_short"] = value
        #elif tag == "JF":
        #    ris_data["journal_full"] = value
        #elif tag == "AN":
        #    ris_data["pmid"] = value
        #elif tag == "U2":
        #    pmcid_match = re.search(r'(PMC\d+)', value)
        #    if pmcid_match:
        #        ris_data["pmcid"] = pmcid_match.group(1)

    return refdata

    #ris_data = {
    #    "authors": [], "title": "", "year": "", "month": "", "day": "",
    #    "doi": "", "pmid": "", "pmcid": "", "journal_short": "", "journal_full": "",
    #    "volume": "", "pages": ""
    #}

# Tests
if __name__ == "__main__":
    FILE = "./references.json"

    refs = None
    with open(FILE, "r") as file:
        refs = json.load(file)

    data = parse_ris(refs[0]["ris"])
    print(data["authors"])

    print(json.dumps(refs[0], indent=4))
    print(json.dumps(data, indent=4))

    #formatted = [{ "id": ref["id"], "data": parse_ris(ref["ris"]) } for ref in refs]
    formatted = [parse_ris(ref["ris"]) for ref in refs]
    print(json.dumps(formatted, indent=4))

































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
