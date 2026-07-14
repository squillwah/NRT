import json
import random
from enum import StrEnum
from refdata import ReferenceComponent

class FormatStyle(StrEnum):
    VANCOUVER = "vancouver"
    APA = "apa"



    ELSEVIER  = "elsevier",
    NATURE    = "nature",
    OXFORD    = "oxford",
    SPRINGER  = "springer",
    CSE       = "cse",
    HARVARD   = "harvard",

class CitationElement(StrEnum):
    AUTHORS          = "authors"
    TITLE            = "title"
    JOURNAL_NAME     = "journal_name"
    PUBLICATION_DATE = "publication_date"
    JOURNAL_META     = "journal_meta"   # Comprises volume, issue, pages/elocator
    IDENTIFIERS      = "identifiers"    # DOI or other database IDs
    

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

# PMC Citing Medicine Guide
# https://www.ncbi.nlm.nih.gov/books/NBK7256/

CE = CitationElement

# Functions which build each element of a citation. Configurable.
class ElementBuilder: 
    def authors(authors, *, etal, etal_apa=False, etal_threshold, delim_authors, delim_initials, delim_lastfirst, initialize, initialize_periods, penultimate_and):       # Some lasts will already be initialized, but may lack periods.
        names = [(a["l"], a["f"]) for a in authors]
        ea = etal_threshold is not None and len(names) > etal_threshold
        if ea: names = names[:etal_threshold] + ([names[-1]] if etal_apa else []) # APA etal mode appends the absolute final author.
        # Transform 'names' into list of author name strings as configured.
        for i, (last, firsts) in enumerate(names):
            if initialize and firsts:    # Not all have first names to be initialized.
                firsts = [i[0].upper()+("." if initialize_periods else "") for i in firsts.split()] # Will we ever get empty from split?    #@TODO Sometimes author lastnames are hyphened, so split at hyphen?
                firsts = delim_initials.join(firsts)
            names[i] = delim_lastfirst.join((last, firsts)) if firsts else last     # Condition avoids trailing ' ' when no first names.
        # Etalify 
        if penultimate_and and not ea:
            names = delim_authors.join(names[:-1]) + penultimate_and + names[-1]
        elif ea:
            if etal_apa: names = delim_authors.join(names[:-1]) + etal + names[-1]  # Smith, J., ... Jane, M.
            else: names = delim_authors.join(names) + etal
        else:
            names = delim_authors.join(names)
        return names

    def journal_name(names, abbreviate):
        return names["short"] if abbreviate else names["full"]

    def journal_meta(vol, iss, page, elocator, styler):
        return styler(vol=vol, iss=iss, page=page, elocator=elocator)  # "stylers" are fstring template functions

    def publication_date(pub, epub, styler):   
        return styler(pub=pub, epub=epub)

    def identifiers(doi, pmid, pmcid, styler): 
        return styler(doi=doi, pmid=pmid, pmcid=pmcid)
   
    # Wrappers around builder methods for unified interface associated with element type constants.
    _COMPONENT_MAP = {
        CitationElement.TITLE:            lambda ref, conf: ref["title"],  #_title(refdata["title"], **settings),
        CitationElement.AUTHORS:          lambda ref, conf: ElementBuilder.authors(ref["authors"], **conf),
        CitationElement.JOURNAL_NAME:     lambda ref, conf: ElementBuilder.journal_name(ref["journal"]["name"], **conf),
        CitationElement.JOURNAL_META:     lambda ref, conf: ElementBuilder.journal_meta(vol=ref["journal"]["volume"], iss=ref["journal"]["issue"], page=ref["journal"]["page"], elocator=ref["journal"]["elocator"], **conf),
        CitationElement.PUBLICATION_DATE: lambda ref, conf: ElementBuilder.publication_date(pub=ref["pub"], epub=ref["epub"], **conf),   # Might be cleaner to nest pub/epub under 'date' instead of flat. Same with identifiers? who cares
        CitationElement.IDENTIFIERS:      lambda ref, conf: ElementBuilder.identifiers(doi=ref["doi"], pmid=ref["pmid"], pmcid=ref["pmcid"], **conf)
    }
   
    # Returns reference to lambdas which call builder functions.
    @classmethod
    def build(cls, element): 
        return cls._COMPONENT_MAP[element]

class Formats:
    # Citations consist of the six CitationElements.
    # ElementBuilder constructs elements, given the reference data source and a builder configuration dict.

    # Formats uses ElementBuilder to create elements configured for a given format. 
    # Formats.ElementStylers are used to customize some ElementBuilder components in place of a config dict. They're basically fstring templates, with some extra conditions for missing components.

    # _LAYOUT defines where how and which CitationElements are included within a particular citation format.
    # _STYLE_CONFIG defines the ElementBuilder configs and stylers to apply to each component for a particular format.

    class ElementStylers:
        # Helper for {y:2015 m:12 d:25} -> 2015 Dec 25
        _MONTHS = { 1:  "Jan", 2:  "Feb", 3:  "Mar",
                    4:  "Apr", 5:  "May", 6:  "Jun",
                    7:  "Jul", 8:  "Aug", 9:  "Sep",
                    10: "Oct", 11: "Nov", 12: "Dec" }
        @classmethod
        def _monthify_date(cls, date):
            styled = ""
            if date["y"]:
                styled = str(date["y"])
                if date["m"]:
                    styled += " " + cls._MONTHS[date["m"]]
                    if date["d"]:
                        styled += " " + str(date["d"])
            return styled
        
        # Vancouver Stylers
        def vancouver_journal_meta(**metadata):
            vol, iss, page, elocator = [metadata[part] for part in ("vol", "iss", "page", "elocator")]
            styled = ""
            styled += str(vol) if vol else ""
            styled += f"({iss})" if iss else ""
            if page["start"] and page["end"]:
                styled += f":{page["start"]}-{page["end"]}"
            elif page["start"] or page["end"]:
                styled += f":{page["start"] if page["start"] else page["end"]}"
            if elocator:
                styled += f":{elocator}"
            return styled
        @classmethod
        def vancouver_publication_date(cls, **pubdates):
            pub, epub = [pubdates[p] for p in ("pub", "epub")]
            date = pub if pub["y"] else epub
            return cls._monthify_date(date)
        def vancouver_identifiers(**idents):
            doi = idents["doi"]
            return f"Available from: doi:{doi["prefix"]}/{doi["suffix"]}"   # Maybe vancouver just shouldn't do DOI? Or it should do URLs instead? Variation needed...
       
        # APA Stylers
        def apa_journal_meta(**metadata):
            vol, iss, page, elocator = [metadata[part] for part in ("vol", "iss", "page", "elocator")]
            styled = ""
            styled += str(vol) if vol else ""
            styled += f"({iss})" if iss else ""
            if page["start"] and page["end"]:
                styled += f", {page["start"]}-{page["end"]}"
            elif page["start"] or page["end"]:
                styled += f", {page["start"] if page["start"] else page["end"]}"
            if elocator:
                styled += f", {elocator}"
            return styled
        def apa_publication_date(**pubdates):
            pub, epub = [pubdates[p] for p in ("pub", "epub")]
            return f"({pub["y"]})" if pub["y"] else f"({epub["y"]})" if epub["y"] else None
        def apa_identifiers(**idents):
            doi = idents["doi"] # We've never encountered a reference without a DOI in the RIS. How would this break if it's absent?
            return f"https://doi.org/{doi["prefix"]}/{doi["suffix"]}"

    # Ordering/combining of rendered citation elements      # This is probabaly where the omission checking would come in?
    def _layout_vancouver(authors, title, journal_name, publication_date, journal_meta, identifiers):   # ! Argument names should match CitationElement strings (so unwrapped CitationElement: "element" dicts can be used)
        return f"{authors}. {title}. {journal_name}. {publication_date};{journal_meta}. {identifiers}"
    def _layout_apa(authors, title, journal_name, publication_date, journal_meta, identifiers):
        return f"{authors} {publication_date}. {title}. {journal_name}, {journal_meta}. {identifiers}"
    _LAYOUT = {
        FormatStyle.VANCOUVER: _layout_vancouver,
        FormatStyle.APA: _layout_apa 
    }

    # Styling configuration of citation elements
    _STYLE_CONFIG = {
        # https://auckland.libguides.com/vancouver/journal-article
        FormatStyle.VANCOUVER: {
            CitationElement.AUTHORS: {
                "etal": ", et al",              # Include comma at start if desired.    ", et al" or " et al"
                "etal_threshold": 6,
                "delim_authors": ", ",
                "delim_initials": "",
                "delim_lastfirst": " ",
                "initialize": True,
                "initialize_periods": False,
                "penultimate_and": "",          # Include comma at start for oxford comma. ", and " or " & " or ", & "  etc.
            },
            CitationElement.TITLE:            { None },  # All supported styles use the default: sentence case.
            CitationElement.JOURNAL_NAME:     { "abbreviate": True },
            CitationElement.JOURNAL_META:     { "styler": ElementStylers.vancouver_journal_meta },
            CitationElement.PUBLICATION_DATE: { "styler": ElementStylers.vancouver_publication_date },
            CitationElement.IDENTIFIERS:      { "styler": ElementStylers.vancouver_identifiers }
        },
        FormatStyle.APA: {
            CitationElement.AUTHORS: {
                "etal": ", ... ",
                "etal_apa": True,               # Appends ... <final_author> instead of an et al. 
                "etal_threshold": 20,
                "delim_authors": ", ",
                "delim_initials": " ",
                "delim_lastfirst": ", ",
                "initialize": True,
                "initialize_periods": True,
                "penultimate_and": " & ",       # Include comma at start for oxford comma. ", and " or " & " or ", & "  etc.

            },
            CitationElement.TITLE:            { None },
            CitationElement.JOURNAL_NAME:     { "abbreviate": False },
            CitationElement.JOURNAL_META:     { "styler": ElementStylers.apa_journal_meta },
            CitationElement.PUBLICATION_DATE: { "styler": ElementStylers.apa_publication_date },
            CitationElement.IDENTIFIERS:      { "styler": ElementStylers.apa_identifiers }
        }
    }
   
    @classmethod
    def build(cls, refdata, style):
        elements = {element: ElementBuilder.build(element)(refdata, cls._STYLE_CONFIG[style][element]) for element in CitationElement}    # @TODO factor the omissions into this.
        print(cls._LAYOUT[style](**elements))

if __name__ == "__main__":
    import h
    refs = h.read_json("refset.json", intkeys=True)
#    Formats.build(refs[88]["data"], FormatStyle.VANCOUVER)
    Formats.build(refs[88]["data"], FormatStyle.VANCOUVER)
    Formats.build(refs[88]["data"], FormatStyle.APA)
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
