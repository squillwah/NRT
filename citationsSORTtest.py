import json
import random

# the thing that Ravi wanted. tracks which components are added to a reference (or tracks it, for better terminology)
PRESENCE_AUTHOR   = 0b0000000001  
PRESENCE_TITLE    = 0b0000000010  
PRESENCE_JOURNAL  = 0b0000000100  
PRESENCE_VOLUME   = 0b0000001000  
PRESENCE_ISSUE    = 0b0000010000  
PRESENCE_PAGE     = 0b0000100000  
PRESENCE_DATE     = 0b0001000000  
PRESENCE_DOI      = 0b0010000000  
PRESENCE_PMID     = 0b0100000000  
PRESENCE_PMCID    = 0b1000000000

# all the individual functions for each of the aforementioned bs citations are listed below.
# we start with elsevier, although for all other strings, it returns the whole thing of using tuples instead of strings.
def compile_elsevier(ref: dict) -> tuple:
    mask = 0
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
    if formatted_authors:
        mask |= PRESENCE_AUTHOR
        if len(formatted_authors) >= 7:
            author_str = ", ".join(formatted_authors[:3]) + ", et al"
        else:
            author_str = ", ".join(formatted_authors)
    else:
        author_str = ""
    if ref.get("title"): mask |= PRESENCE_TITLE
    if ref["journal"]["name"].get("short"): mask |= PRESENCE_JOURNAL
    if ref["journal"].get("volume"): mask |= PRESENCE_VOLUME   
    issue_str = ""
    if ref["journal"].get("issue"):
        mask |= PRESENCE_ISSUE
        issue_str = f"({ref['journal']['issue']})" 
    p_data = ref["journal"]["page"]
    pages = ""
    if p_data.get("start"):
        mask |= PRESENCE_PAGE
        pages = p_data.get("start", "") if p_data.get("start") == p_data.get("end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"     
    if ref["pub"].get("y"): mask |= PRESENCE_DATE
    if ref.get("doi"): mask |= PRESENCE_DOI
    if ref.get("pmid"): mask |= PRESENCE_PMID
    if ref.get("pmcid"): mask |= PRESENCE_PMCID
    final_str = f"{author_str}. {ref['title']}. {ref['journal']['name']['short']}. {ref['pub']['y']};{ref['journal']['volume']}{issue_str}:{pages}. doi:{ref['doi']}"
    return final_str, mask


def compile_nature(ref: dict) -> tuple:
    mask = 0
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
    if formatted_authors:
        mask |= PRESENCE_AUTHOR
        if len(formatted_authors) > 5:
            author_str = f"{formatted_authors[0]}, et al"
        elif len(formatted_authors) > 1:
            author_str = ", ".join(formatted_authors[:-1]) + " & " + formatted_authors[-1]
        else:
            author_str = formatted_authors[0]
    else:
        author_str = ""   
    if ref.get("title"): mask |= PRESENCE_TITLE
    if ref["journal"]["name"].get("short"): mask |= PRESENCE_JOURNAL
    if ref["journal"].get("volume"): mask |= PRESENCE_VOLUME
    if ref["journal"].get("issue"): mask |= PRESENCE_ISSUE
    p_data = ref["journal"]["page"]
    pages = ""
    if p_data.get("start"):
        mask |= PRESENCE_PAGE
        pages = p_data.get("start", "") if p_data.get("start") == p_data.get("end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}" 
    if ref["pub"].get("y"): mask |= PRESENCE_DATE
    if ref.get("doi"): mask |= PRESENCE_DOI
    if ref.get("pmid"): mask |= PRESENCE_PMID
    if ref.get("pmcid"): mask |= PRESENCE_PMCID
    final_str = f"{author_str}. {ref['title']}. <i>{ref['journal']['name']['short']}</i> <b>{ref['journal']['volume']}</b>, {pages} ({ref['pub']['y']})."
    return final_str, mask


def compile_oxford(ref: dict) -> tuple:
    mask = 0
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
    if formatted_authors:
        mask |= PRESENCE_AUTHOR
        if len(formatted_authors) > 1:
            author_str = ", ".join(formatted_authors[:-1]) + " and " + formatted_authors[-1]
        else:
            author_str = formatted_authors[0]
    else:
        author_str = ""
    if ref.get("title"): mask |= PRESENCE_TITLE
    if ref["journal"]["name"].get("short"): mask |= PRESENCE_JOURNAL
    if ref["journal"].get("volume"): mask |= PRESENCE_VOLUME 
    issue_str = ""
    if ref["journal"].get("issue"):
        mask |= PRESENCE_ISSUE
        issue_str = f"({ref['journal']['issue']})"
    p_data = ref["journal"]["page"]
    pages = ""
    if p_data.get("start"):
        mask |= PRESENCE_PAGE
        pages = p_data.get("start", "") if p_data.get("start") == p_data.get("end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"
    if ref["pub"].get("y"): mask |= PRESENCE_DATE
    if ref.get("doi"): mask |= PRESENCE_DOI
    if ref.get("pmid"): mask |= PRESENCE_PMID
    if ref.get("pmcid"): mask |= PRESENCE_PMCID
    final_str = f"{author_str}. ({ref['pub']['y']}) {ref['title']}. <i>{ref['journal']['name']['short']}</i>, <i>{ref['journal']['volume']}</i>{issue_str}, {pages}. https://doi.org/{ref['doi']}"
    return final_str, mask


def compile_springer(ref: dict) -> tuple:
    mask = 0
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
    if formatted_authors:
        mask |= PRESENCE_AUTHOR
        if len(formatted_authors) >= 7:
            author_str = ", ".join(formatted_authors[:3]) + ", et al"
        else:
            author_str = ", ".join(formatted_authors)
    else:
        author_str = ""
    if ref.get("title"): mask |= PRESENCE_TITLE
    if ref["journal"]["name"].get("short"): mask |= PRESENCE_JOURNAL
    if ref["journal"].get("volume"): mask |= PRESENCE_VOLUME
    if ref["journal"].get("issue"): mask |= PRESENCE_ISSUE
    p_data = ref["journal"]["page"]
    pages = ""
    if p_data.get("start"):
        mask |= PRESENCE_PAGE
        pages = p_data.get("start", "") if p_data.get("start") == p_data.get("end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"
    if ref["pub"].get("y"): mask |= PRESENCE_DATE
    if ref.get("doi"): mask |= PRESENCE_DOI
    if ref.get("pmid"): mask |= PRESENCE_PMID
    if ref.get("pmcid"): mask |= PRESENCE_PMCID
    final_str = f"{author_str}. {ref['title']}. <i>{ref['journal']['name']['short']}</i>. {ref['pub']['y']}; {ref['journal']['volume']}: {pages}. doi: {ref['doi']}"
    return final_str, mask


def compile_cse(ref: dict) -> tuple:
    mask = 0
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
    if formatted_authors:
        mask |= PRESENCE_AUTHOR
        if len(formatted_authors) >= 11:
            author_str = ", ".join(formatted_authors[:10]) + ", et al"
        else:
            author_str = ", ".join(formatted_authors)
    else:
        author_str = "" 
    if ref.get("title"): mask |= PRESENCE_TITLE
    if ref["journal"]["name"].get("short"): mask |= PRESENCE_JOURNAL
    if ref["journal"].get("volume"): mask |= PRESENCE_VOLUME
    issue_str = ""
    if ref["journal"].get("issue"):
        mask |= PRESENCE_ISSUE
        issue_str = f"({ref['journal']['issue']})" 
    p_data = ref["journal"]["page"]
    pages = ""
    if p_data.get("start"):
        mask |= PRESENCE_PAGE
        pages = p_data.get("start", "") if p_data.get("start") == p_data.get("end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"
    if ref["pub"].get("y"): mask |= PRESENCE_DATE
    if ref.get("doi"): mask |= PRESENCE_DOI
    if ref.get("pmid"): mask |= PRESENCE_PMID
    if ref.get("pmcid"): mask |= PRESENCE_PMCID
    final_str = f"{author_str}. {ref['title']}. {ref['journal']['name']['short']}. {ref['pub']['y']};{ref['journal']['volume']}{issue_str}:{pages}."
    return final_str, mask
    
def compile_harvard(ref: dict) -> tuple:
    mask = 0
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
        
    if formatted_authors:
        mask |= PRESENCE_AUTHOR
        if len(formatted_authors) > 1:
            author_str = ", ".join(formatted_authors[:-1]) + " and " + formatted_authors[-1]
        else:
            author_str = formatted_authors[0]
    else:
        author_str = ""
        
    if ref.get("title"): mask |= PRESENCE_TITLE
    if ref["journal"]["name"].get("full"): mask |= PRESENCE_JOURNAL
    if ref["journal"].get("volume"): mask |= PRESENCE_VOLUME
    
    issue_str = ""
    if ref["journal"].get("issue"):
        mask |= PRESENCE_ISSUE
        issue_str = f"({ref['journal']['issue']})"
        
    p_data = ref["journal"]["page"]
    pages = ""
    if p_data.get("start"):
        mask |= PRESENCE_PAGE
        pages = p_data.get("start", "") if p_data.get("start") == p_data.get("end") else f"{p_data.get('start', '')}–{p_data.get('end', '')}"
        
    if ref["pub"].get("y"): mask |= PRESENCE_DATE
    if ref.get("doi"): mask |= PRESENCE_DOI
    if ref.get("pmid"): mask |= PRESENCE_PMID
    if ref.get("pmcid"): mask |= PRESENCE_PMCID

    final_str = f"{author_str} ({ref['pub']['y']}). '{ref['title']}', <i>{ref['journal']['name']['full']}</i>, {ref['journal']['volume']}{issue_str}, pp. {pages}. doi: {ref['doi']}."
    return final_str, mask


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
    selected_reference = random.choice(data_pool)

    # calls the modified functions and unpack their tuple vars
    els_str, els_mask = compile_elsevier(selected_reference)
    nat_str, nat_mask = compile_nature(selected_reference)
    oxf_str, oxf_mask = compile_oxford(selected_reference)
    spr_str, spr_mask = compile_springer(selected_reference)
    cse_str, cse_mask = compile_cse(selected_reference)
    har_str, har_mask = compile_harvard(selected_reference)
    output_payload = {
        "selected_reference_title": selected_reference["title"],
        "doi": selected_reference["doi"],
        "pmid": selected_reference["pmid"],
        "citations": {
            "elsevier": {
                "string": els_str,
                "components_bitmask_int": els_mask,
                "components_bitmask_bin": f"0b{els_mask:010b}"
            },
            "nature": {
                "string": nat_str,
                "components_bitmask_int": nat_mask,
                "components_bitmask_bin": f"0b{nat_mask:010b}"
            },
            "oxford": {
                "string": oxf_str,
                "components_bitmask_int": oxf_mask,
                "components_bitmask_bin": f"0b{oxf_mask:010b}"
            },
            "springer_vancouver": {
                "string": spr_str,
                "components_bitmask_int": spr_mask,
                "components_bitmask_bin": f"0b{spr_mask:010b}"
            },
            "cse": {
                "string": cse_str,
                "components_bitmask_int": cse_mask,
                "components_bitmask_bin": f"0b{cse_mask:010b}"
            },
            "harvard": {
                "string": har_str,
                "components_bitmask_int": har_mask,
                "components_bitmask_bin": f"0b{har_mask:010b}"
            }
        }
    }
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)
    print(f"[Success] Done. Look in '{output_filename}'")

if __name__ == "__main__":
    run_random_citation_builder("refdata.json", "mutationcombinedoutput.json")
