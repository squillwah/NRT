import json
import random

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
    return f"{author_str}. {ref['title']}. {ref['journal']['name']['short']}. {ref['pub']['y']};{ref['journal']['volume']}{issue_str}:{pages}. doi:{ref['doi']}"

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
    return f"{author_str}. ({ref['pub']['y']}) {ref['title']}. <i>{ref['journal']['name']['short']}</i>, <i>{ref['journal']['volume']}</i>{issue_str}, {pages}. https://doi.org/{ref['doi']}"

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

    return f"{author_str}. {ref['title']}. <i>{ref['journal']['name']['short']}</i>. {ref['pub']['y']}; {ref['journal']['volume']}: {pages}. doi: {ref['doi']}"

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
    return f"{author_str} ({ref['pub']['y']}). '{ref['title']}', <i>{ref['journal']['name']['full']}</i>, {ref['journal']['volume']}{issue_str}, pp. {pages}. doi: {ref['doi']}."


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