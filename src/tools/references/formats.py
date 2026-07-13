import json
import random
from enum import StrEnum

class FormatStyle(StrEnum):
    ELSEVIER  = "elsevier",
    NATURE    = "nature",
    OXFORD    = "oxford",
    SPRINGER  = "springer",
    CSE       = "cse",
    HARVARD   = "harvard",
    VANCOUVER = "vancouver"

# Standards
# AMA
# Vancouver
# NLM
# APA

# Journal Variations
# Nature
# Science
# Elsevier
# Springer

#Vancouver / NLM
#PubMed
#AMA
#ICMJE
#Nature
#Cell Press
#Science (AAAS)
#PNAS
#Elsevier Vancouver
#Springer Nature
#Wiley
#eLife
#Oxford University Press
#ACS (biochemistry journals)
# IEEE

from refdata import ReferenceComponent as RC

# PMC Citing Medicine Guide
# https://www.ncbi.nlm.nih.gov/books/NBK7256/

class Formats:
    _STYLE_CONFIGS = {
        # How the author list is styled,.
        FormatStyle.VANCOUVER: {
            RC.AUTHORS: {
                "etal": ", et al",              # Include comma at start if desired.    ", et al" or " et al"
                "etal_threshold": 6,
                "delim_authors": ", ",
                "delim_initials": "",
                "delim_lastfirst": " ",
                "initialize": True,
                "initialize_periods": False,
                "penultimate_and": "",          # Include comma at start for oxford comma. ", and " or " & " or ", & "  etc.
            },
            RC.JOURNAL_NAME: "short",    # Or 'full'
            "ORDER": [RC.AUTHORS, RC.TITLE]
        }
    }
        
    #_COMPONENT_PROCESSING = {
    #    RC.AUTHORS:             Formats._authorize
    #    RC.TITLE:               lambda title: title
    #    RC.JOURNAL_NAME:        lambda 
    #    RC.JOURNAL_VOLUME:  
    #    RC.JOURNAL_ISSUE:   
    #    RC.JOURNAL_PAGE:    
    #    RC.ELOCATOR:        
    #    RC.PUBLICATION_DATE:
    #    RC.DOI:             
    #    RC.PMID:            
    #    RC.PMCID:           
    #}

    @staticmethod
    def _authorize(authors, *, etal, etal_threshold, delim_authors, delim_initials, delim_lastfirst, initialize, initialize_periods, penultimate_and):       # Some lasts will already be initialized, but may lack periods.
        names = [(a["l"], a["f"]) for a in authors]
        ea = etal_threshold is not None and len(names) > etal_threshold
        if ea: names = names[:etal_threshold]
        for i, (last, firsts) in enumerate(names):
            if initialize and firsts:    # Not all have first names to be initialized.
                firsts = [i[0].upper()+("." if initialize_periods else "") for i in firsts.split()] # Will we ever get empty from split?
                firsts = delim_initials.join(firsts)
            names[i] = delim_lastfirst.join((last, firsts)) if firsts else last     # Condition avoids trailing ' ' when no first names.
        if penultimate_and and not ea:
            names = delim_authors.join(names[:-1]) + penultimate_and + names[-1]
        else:
            names = delim_authors.join(names) + etal*ea
        return names

    @classmethod
    def build(cls, refdata, style):    # components: list[ReferenceComponent]
        # Combine given components in sequential order
        _COMPONENT_PROCESSING = {
            RC.AUTHORS:             lambda rd, s: cls._authorize(refdata["authors"], **cls._STYLE_CONFIGS[s][RC.AUTHORS]),
            RC.TITLE:               lambda rd, s: rd["title"], # Special processing?
            RC.JOURNAL_NAME:        lambda rd, s: rd["journal"]["name"][cls._STYLE_CONFIGS[s][RC.JOURNAL_NAME]],
            RC.JOURNAL_VOLUME:      lambda rd, s: rd["journal"]["volume"],  # Special styling ? (Paranthesis, semicolons and stuff?)
            RC.JOURNAL_ISSUE:       lambda rd, s: rd["journal"]["issue"],
            RC.JOURNAL_PAGE:        lambda rd, s: str(rd["journal"]["page"]["start"]) + "-" + str(rd["journal"]["page"]["end"]),
            RC.ELOCATOR:            lambda rd, s: rd["journal"]["elocator"],
            RC.PUBLICATION_DATE:    lambda rd, s: rd["pub"], # or rd["epub"] ? Hopefully deteremined by style. As well as y/m/d.
            RC.DOI:                 lambda rd, s: rd["doi"]["prefix"] + "/" + rd["doi"]["suffix"], # Style should determine https:// inclusion etc.
            RC.PMID:                lambda rd, s: rd["pmid"],
            RC.PMCID:               lambda rd, s: rd["pmcid"]
        }

        for c in _COMPONENT_PROCESSING:
            print(_COMPONENT_PROCESSING[c](refdata, style))

import h
if __name__ == "__main__":
    refs = h.read_json("refset.json", intkeys=True)
    Formats.build(refs[88]["data"], FormatStyle.VANCOUVER)
    #Formats._authorize(ass, **Formats._STYLE_CONFIGS[FormatStyle.VANCOUVER]["authors"])

"""
# all the individual functions for each of the aforementioned bs citations are listed below.
def compile_elsevier(ref: dict) -> str:
    formatted_authors = []
    for auth in ref["authors"]:
        last = auth.get("l", "").strip()
        first = auth.get("f", "").strip()
        if last and not first:
            formatted_authors.append(last)
            continue
        parts = first.replace("-", " ").split()
        initials = "".join([p[0].upper() for p in parts if p])
        formatted_authors.append(f"{last} {initials}")
    author_str = ", ".join(formatted_authors)
    p_data = ref["journal"]["page"]
    pages = p_data.get("start", "") if p_data.get("start") == p_data.get(
        "end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"

    issue_str = f"({ref['journal']['issue']})" if ref["journal"]["issue"] else ""
    return f"{author_str}. {ref['title']}. {ref['journal']['name']['short']}. {ref['pub']['y']};{ref['journal']['volume']}{issue_str}:{pages}. doi:{"/".join(ref['doi'].values())}"

def compile_nature(ref: dict) -> str:
    formatted_authors = []
    for auth in ref["authors"]:
        last = auth.get("l", "").strip()
        first = auth.get("f", "").strip()
        if last and not first:
            formatted_authors.append(last)
            continue
        parts = first.replace("-", " ").split()
        dotted = ".".join([p[0].upper() for p in parts if p]) + "." if parts else ""
        formatted_authors.append(f"{last}, {dotted}")
    if len(formatted_authors) > 5:
        author_str = f"{formatted_authors[0]}, et al"
    elif len(formatted_authors) > 1:
        author_str = ", ".join(formatted_authors[:-1]) + " & " + formatted_authors[-1]
    else:
        author_str = formatted_authors[0] if formatted_authors else ""
    p_data = ref["journal"]["page"]
    pages = p_data.get("start", "") if p_data.get("start") == p_data.get(
        "end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"

    return f"{author_str}. {ref['title']}. <i>{ref['journal']['name']['short']}</i> <b>{ref['journal']['volume']}</b>, {pages} ({ref['pub']['y']})."

def compile_oxford(ref: dict) -> str:
    formatted_authors = []
    for auth in ref["authors"]:
        last = auth.get("l", "").strip()
        first = auth.get("f", "").strip()
        if last and not first:
            formatted_authors.append(last)
            continue
        parts = first.replace("-", " ").split()
        dotted = ".".join([p[0].upper() for p in parts if p]) + "." if parts else ""
        formatted_authors.append(f"{last}, {dotted}")
    if len(formatted_authors) > 1:
        author_str = ", ".join(formatted_authors[:-1]) + " and " + formatted_authors[-1]
    else:
        author_str = formatted_authors[0] if formatted_authors else ""
    p_data = ref["journal"]["page"]
    pages = p_data.get("start", "") if p_data.get("start") == p_data.get(
        "end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"

    issue_str = f"({ref['journal']['issue']})" if ref["journal"]["issue"] else ""
    return f"{author_str}. ({ref['pub']['y']}) {ref['title']}. <i>{ref['journal']['name']['short']}</i>, <i>{ref['journal']['volume']}</i>{issue_str}, {pages}. https://doi.org/{"/".join(ref['doi'].values())}"

def compile_springer(ref: dict) -> str:
    formatted_authors = []
    for auth in ref["authors"]:
        last = auth.get("l", "").strip()
        first = auth.get("f", "").strip()
        if last and not first:
            formatted_authors.append(last)
            continue
        parts = first.replace("-", " ").split()
        initials = "".join([p[0].upper() for p in parts if p])
        formatted_authors.append(f"{last} {initials}")
    author_str = ", ".join(formatted_authors)
    p_data = ref["journal"]["page"]
    pages = p_data.get("start", "") if p_data.get("start") == p_data.get(
        "end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"

    return f"{author_str}. {ref['title']}. <i>{ref['journal']['name']['short']}</i>. {ref['pub']['y']}; {ref['journal']['volume']}: {pages}. doi: {"/".join(ref['doi'].values())}"

def compile_cse(ref: dict) -> str:
    formatted_authors = []
    for auth in ref["authors"]:
        last = auth.get("l", "").strip()
        first = auth.get("f", "").strip()
        if last and not first:
            formatted_authors.append(last)
            continue
        parts = first.replace("-", " ").split()
        initials = "".join([p[0].upper() for p in parts if p])
        formatted_authors.append(f"{last} {initials}")
    author_str = ", ".join(formatted_authors)

    p_data = ref["journal"]["page"]
    pages = p_data.get("start", "") if p_data.get("start") == p_data.get(
        "end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"

    issue_str = f"({ref['journal']['issue']})" if ref["journal"]["issue"] else ""
    return f"{author_str}. {ref['title']}. {ref['journal']['name']['short']}. {ref['pub']['y']};{ref['journal']['volume']}{issue_str}:{pages}."

def compile_harvard(ref: dict) -> str:
    formatted_authors = []
    for auth in ref["authors"]:
        last = auth.get("l", "").strip()
        first = auth.get("f", "").strip()
        if last and not first:
            formatted_authors.append(last)
            continue
        parts = first.replace("-", " ").split()
        dotted = ".".join([p[0].upper() for p in parts if p]) + "." if parts else ""
        formatted_authors.append(f"{last}, {dotted}")
    if len(formatted_authors) > 1:
        author_str = ", ".join(formatted_authors[:-1]) + " and " + formatted_authors[-1]
    else:
        author_str = formatted_authors[0] if formatted_authors else ""
    p_data = ref["journal"]["page"]
    pages = p_data.get("start", "") if p_data.get("start") == p_data.get(
        "end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"

    issue_str = f"({ref['journal']['issue']})" if ref["journal"]["issue"] else ""
    return f"{author_str} ({ref['pub']['y']}). '{ref['title']}', <i>{ref['journal']['name']['full']}</i>, {ref['journal']['volume']}{issue_str}, pp. {pages}. doi: {"/".join(ref['doi'].values())}."


STYLE_COMPILE = {
    FormatStyle.ELSEVIER: compile_elsevier,
    FormatStyle.NATURE:   compile_nature,
    FormatStyle.OXFORD:   compile_oxford,
    FormatStyle.SPRINGER: compile_springer,
    FormatStyle.CSE:      compile_cse,
    FormatStyle.HARVARD:  compile_harvard
}

# Return dict with all formats baked.
def compile_all(refdata):
    return {f: STYLE_COMPILE[f](refdata) for f in FormatStyle}

# function to grab refdata.json, grab a random dictionary from it, and then output the different citations
def run_random_citation_builder(input_filename: str, output_filename: str):
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            data_pool = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not locate '{input_filename}' in this folder directory.")
        return
    if not data_pool:
        print("Error: Input data pool file is empty.")
        return
    # just for that free grab thingymabob
    selected_reference = random.choice(data_pool)

    # hands off selected dictionary to function
    output_payload = {
        "selected_reference_title": selected_reference["title"],
        "doi": selected_reference["doi"],
        "pmid": selected_reference["pmid"],
        "citations": {
            "elsevier": compile_elsevier(selected_reference),
            "nature": compile_nature(selected_reference),
            "oxford": compile_oxford(selected_reference),
            "springer_vancouver": compile_springer(selected_reference),
            "cse": compile_cse(selected_reference),
            "harvard": compile_harvard(selected_reference)
        }
    }
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)
    print(f"[Success] Done. Look in '{output_filename}'")

if __name__ == "__main__":
    run_random_citation_builder("refdata.json", "mutationcombinedoutput.json")
"""
