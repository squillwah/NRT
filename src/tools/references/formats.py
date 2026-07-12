import json
import random
from enum import StrEnum

class FormatStyle(StrEnum):
    ELSEVIER  = "elsevier",
    NATURE    = "nature",
    OXFORD    = "oxford",
    SPRINGER  = "springer",
    CSE       = "cse",
    HARVARD   = "harvard"

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

class Formats:
    _AUTHOR_PRESETS = {
        "vancouver": {
            "ea_threshold": 6,
            "delim_authors": ", ",
            "delim_initials": "",
            "delim_lastfirst": " ",
            "initialize": True,
            "initialize_periods": False
        }
    }

    @staticmethod
    def authorize(authors, *, ea_threshold=None, delim_authors, delim_initials, delim_lastfirst, initialize, initialize_periods):       # Some lasts will already be initialized, but may lack periods.
        names = [(a["l"], a["f"]) for a in authors]
        ea = ea_threshold is not None and len(names) > ea_threshold
        if ea: names = names[:ea_threshold]
        for i, (last, firsts) in enumerate(names):
            if initialize and firsts:    # Not all have first names to be initialized.
                firsts = [i[0].upper()+("." if initialize_periods else "") for i in firsts.split()] # Will we ever get empty from split?
                firsts = delim_initials.join(firsts)
            names[i] = delim_lastfirst.join((last, firsts)) if firsts else last     # Condition avoids trailing ' ' when no first names.
        if ea: names.append("et al")
        names = delim_authors.join(names)
        print(names)
        #print(locals())
        #formatted = ([None] * ea_threshold + ["et al"]) if ea_threshold is not None and len(names) > ea_threshold else ([None] * len(names))
        #print(formatted)

ass = [
      {
        "l": "Akbari",
        "f": "R"
      },
      {
        "l": "de Araujo Azevedo",
        "f": "L O"
      },
      {
        "l": "Baker",
        "f": "C J"
      },
      {
        "l": "Bertsche",
        "f": "W"
      },
      {
        "l": "Bhatt",
        "f": "N M"
      },
      {
        "l": "Bonomi",
        "f": "G"
      },
      {
        "l": "Capra",
        "f": "A"
      },
      {
        "l": "Carli",
        "f": "I"
      },
      {
        "l": "L Cesar",
        "f": "C"
      },
      {
        "l": "Charlton",
        "f": "M"
      },
      {
        "l": "Cridland Mathad",
        "f": "A"
      },
      {
        "l": "Del Vincio",
        "f": "A"
      },
      {
        "l": "Duque Quiceno",
        "f": "D"
      },
      {
        "l": "Eriksson",
        "f": "S"
      },
      {
        "l": "Evans",
        "f": "A"
      },
      {
        "l": "Fajans",
        "f": "J"
      },
      {
        "l": "Friesen",
        "f": "T"
      },
      {
        "l": "Fujiwara",
        "f": "M C"
      },
      {
        "l": "Golino",
        "f": "L M"
      },
      {
        "l": "Gomes Gon\u00e7alves",
        "f": "M B"
      },
      {
        "l": "Hangst",
        "f": "J S"
      },
      {
        "l": "Hayden",
        "f": "M E"
      },
      {
        "l": "Heidari",
        "f": "P"
      },
      {
        "l": "Hodgkinson",
        "f": "D"
      },
      {
        "l": "Isaac",
        "f": "C A"
      },
      {
        "l": "Jones",
        "f": "S A"
      },
      {
        "l": "Jonsell",
        "f": "S"
      },
      {
        "l": "Madsen",
        "f": "N"
      },
      {
        "l": "Marshall",
        "f": "V R"
      },
      {
        "l": "McKenna",
        "f": "J T K"
      },
      {
        "l": "Momose",
        "f": "T"
      },
      {
        "l": "Nauta",
        "f": "J"
      },
      {
        "l": "Oliveira",
        "f": "A N"
      },
      {
        "l": "Powell",
        "f": "A"
      },
      {
        "l": "Rasmussen",
        "f": "C \u00d8"
      },
      {
        "l": "Robertson-Brown",
        "f": "T"
      },
      {
        "l": "Robicheaux",
        "f": "F"
      },
      {
        "l": "Sacramento",
        "f": "R L"
      },
      {
        "l": "Sarid",
        "f": "E"
      },
      {
        "l": "Schoonwater",
        "f": "J"
      },
      {
        "l": "Silveira",
        "f": "D M"
      },
      {
        "l": "Singh",
        "f": "J"
      },
      {
        "l": "Smith",
        "f": "G"
      },
      {
        "l": "So",
        "f": "C"
      },
      {
        "l": "Stracka",
        "f": "S"
      },
      {
        "l": "Suh",
        "f": "J"
      },
      {
        "l": "Swadling",
        "f": "A G"
      },
      {
        "l": "Tharp",
        "f": "T D"
      },
      {
        "l": "Thompson",
        "f": "K A"
      },
      {
        "l": "Thompson",
        "f": "R I"
      },
      {
        "l": "Thorpe-Woods",
        "f": "E"
      },
      {
        "l": "Uribe Jimenez",
        "f": "A J"
      },
      {
        "l": "Urioni",
        "f": "M"
      },
      {
        "l": "van de Werf",
        "f": "D P"
      },
      {
        "l": "Wilson",
        "f": "S G"
      },
      {
        "l": "ALPHA Collaboration",
        "f": ""
      },
      {
        "l": "Woosaree",
        "f": "P"
      },
      {
        "l": "Wurtele",
        "f": "J S"
      }
    ]



Formats.authorize(ass, **Formats._AUTHOR_PRESETS["vancouver"])

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
