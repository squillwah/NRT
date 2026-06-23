import json
import re


def parse_ris(ris_string: str) -> dict:
    ris_data = {
        "authors": [], "title": "", "year": "", "month": "", "day": "",
        "doi": "", "pmid": "", "pmcid": "", "journal_short": "", "journal_full": "",
        "volume": "", "pages": ""
    }
    # line cleaner
    for line in ris_string.splitlines():
        line = line.strip()
        if not line:
            continue

        # regular expressions to split on tags regardless of weird non-breaking space characters
        match = re.split(r'\s+-\s+', line, maxsplit=1)
        if len(match) < 2:
            continue
        tag, value = match[0].strip(), match[1].strip()
        if tag == "AU":
            ris_data["authors"].append(value)
        elif tag == "T1":
            ris_data["title"] = value.rstrip(".")
        elif tag == "Y1":
            date_parts = value.split('/')
            if len(date_parts) >= 1: ris_data["year"] = date_parts[0]
            if len(date_parts) >= 2: ris_data["month"] = date_parts[1]
            if len(date_parts) >= 3: ris_data["day"] = date_parts[2]
        elif tag == "DO":
            ris_data["doi"] = value
        elif tag == "VL":
            ris_data["volume"] = value
        elif tag == "SP":
            ris_data["pages"] = value
        elif tag == "J2":
            ris_data["journal_short"] = value
        elif tag == "JF":
            ris_data["journal_full"] = value
        elif tag == "AN":
            ris_data["pmid"] = value
        elif tag == "U2":
            pmcid_match = re.search(r'(PMC\d+)', value)
            if pmcid_match:
                ris_data["pmcid"] = pmcid_match.group(1)

    if ris_data["pmid"]:
        ris_data["id"] = f"pmid:{ris_data['pmid']}"
    else:
        ris_data["id"] = "unknown_id"

    return ris_data
# relevant for the proper construction of the months
def get_month_abbr(month_str: str) -> str:
    months = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
        "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    return months.get(month_str, "Jun")

# builds the ama portion
def build_ama(data: dict) -> str:
    formatted_authors = []
    for author in data["authors"]:
        if "," in author:
            last, first = author.split(",", 1)
            initials = "".join([i[0] for i in first.strip().split()])
            formatted_authors.append(f"{last.strip()} {initials}")
        else:
            formatted_authors.append(author)
    if len(formatted_authors) >= 7: # because ama really wants to get specific. SIX SEVENNNNNNN
        author_str = ", ".join(formatted_authors[:3]) + ", et al"
    else:
        author_str = ", ".join(formatted_authors)
    month_lbl = get_month_abbr(data["month"])
    day_lbl = data["day"].lstrip('0') if data["day"] else ""
    return f"{author_str}. {data['title']}. <i>{data['journal_short']}</i>. {data['year']};{data['volume']}:{data['pages']}. Published {data['year']} {month_lbl} {day_lbl}. doi:{data['doi']}"

# build apa with parameters.
def build_apa(data: dict) -> str:
    formatted_authors = []
    for author in data["authors"]:
        if "," in author:
            last, first = author.split(",", 1)
            initials = ". ".join([i[0] for i in first.strip().split()]) + "."
            formatted_authors.append(f"{last.strip()}, {initials}")
        else:
            formatted_authors.append(author)
    if len(formatted_authors) > 1:
        author_str = ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]
    else:
        author_str = formatted_authors[0] if formatted_authors else ""
    return f"{author_str} ({data['year']}). {data['title']}. <i>{data['journal_full']}</i>, <i>{data['volume']}</i>, {data['pages']}. https://doi.org/{data['doi']}"

# build mla with parameters
def build_mla(data: dict) -> str:
    author_str = ""
    if data["authors"]:
        first_author = data["authors"][0]
        if len(data["authors"]) > 1:
            author_str = f"{first_author.strip()} et al"
        else:
            author_str = first_author.strip()
    month_lbl = get_month_abbr(data["month"])
    day_lbl = data["day"].lstrip('0') if data["day"] else ""
    return f"{author_str}. \u201c{data['title']}.\u201d <i>{data['journal_full']}</i> vol. {data['volume']} {data['pages']}. {day_lbl} {month_lbl}. {data['year']}, doi:{data['doi']}"

# unlike ama, this just lists authors without et al.
def build_nlm(data: dict) -> str:
    formatted_authors = []
    for author in data["authors"]:
        if "," in author:
            last, first = author.split(",", 1)
            initials = "".join([i[0] for i in first.strip().split()])
            formatted_authors.append(f"{last.strip()} {initials}")
        else:
            formatted_authors.append(author)
    author_str = ", ".join(formatted_authors)
    month_lbl = get_month_abbr(data["month"])
    day_lbl = data["day"].lstrip('0') if data["day"] else ""
    return f"{author_str}. {data['title']}. {data['journal_short']}. {data['year']} {month_lbl} {day_lbl};{data['volume']}:{data['pages']}. doi: {data['doi']}. PMID: {data['pmid']}; PMCID: {data['pmcid']}."


# finds and opens the file
if __name__ == "__main__":
    try:
        with open("referencesTEST.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print("Could not find referencesTEST.json file.")
        exit()
    first_entry = raw_data[0]
    parsed_variables = parse_ris(first_entry.get("ris", ""))
    output = {
        "id": parsed_variables["id"],
        "ama": build_ama(parsed_variables),
        "apa": build_apa(parsed_variables),
        "mla": build_mla(parsed_variables),
        "nlm": build_nlm(parsed_variables),
        "ris": first_entry.get("ris")
    }
    print("- Non-altered Citation Data Generation Verification -")
    print(json.dumps(output, indent=2))

    # creates the file and throws all of the previous stuff into it.
    output_filename = "mutationtest2file.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\n[Success] Output document '{output_filename}' has been created!")