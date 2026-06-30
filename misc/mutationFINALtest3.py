# four packages are used for this. json is imported to finalize the document that contains all of the permutations. the
# importing of "re" allows for the use of regex, which is what we used for more intricate text pattern analysis in
# later steps. import random and copy both randomize certain aspects of randomization for the permutations, along with
# the duplication of text in other sections.
import json
import re
import random
import copy

# Ravi wanted this. this will allow for better editing in the future.
MASK_REAL = 0b0000
MASK_AUTHOR_SWAP = 0b0001
MASK_TITLE_TYPO = 0b0010
MASK_YEAR_SHIFT = 0b0100
MASK_DOI_CORRUPT = 0b1000

# begin by parsing data through here, properly dividing it as we go. gives it everything, including pmcid because
# nlm is picky about that shit. >:(
def parse_ris(ris_string: str) -> dict:
    ris_data = {
        "authors": [], "title": "", "year": "", "month": "", "day": "",
        "doi": "", "pmid": "", "pmcid": "", "journal_short": "", "journal_full": "",
        "volume": "", "pages": ""
    }
    for line in ris_string.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.split(r'\s+-\s+', line, maxsplit=1) # string split when surrounded by hyphens.
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

def get_month_abbr(month_str: str) -> str: # month and year construction for when it creates the ama/apa/mla/nlm copies
    months = {  # line SIX SEVENNNNNNNNNNNNNNNNNNNN
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
        "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    return months.get(month_str, "Jun") # fallback just in case something decides to act up.


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

# builds apa with parameters.
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

# builds mla with parameters.
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

# previously, the file opening portion of the code was here, but that was thrown to the end because we now need space to
# define what the permutations look like, which is very important.
# begin with defining the typos. It switches the characters of two portions within the title in the index of 1.
def introduce_typo(text: str) -> str:
    if len(text) < 2: return text
    idx = random.randint(0, len(text) - 2)
    text_list = list(text)
    text_list[idx], text_list[idx + 1] = text_list[idx + 1], text_list[idx]
    return "".join(text_list)

# defines the "error" in question by changing the position of the first and second author (in index values 0 and 1).
def mutate_author_swap(authors: list) -> list:
    if len(authors) >= 2:
        new_authors = copy.deepcopy(authors)
        new_authors[0], new_authors[1] = new_authors[1], new_authors[0]
        return new_authors
    return authors

# uses a random number generator to pick 1-2 years forwards or backwards for the date of the document.
def mutate_year_shift(year_str: str) -> str:
    try:
        return str(int(year_str) + random.choice([-2, -1, 1, 2]))
    except ValueError:
        return year_str

# note: i moved the doi corruption into the next portion of the code only because it's not so large that it requires its
# own function.

# beginning section of the permute reference, such as how it is known that a permutation is occurring.
def permute_reference(original_entry: dict, bitmask_settings: int) -> dict:
    """Parses citation variables, processes bitwise mutations, and bakes string parameters."""
    parsed_vars = parse_ris(original_entry.get("ris", ""))
    mutations_applied_log = []

    # checks for bitwise flags using bitwise and operations. this one is for author swap.
    if (bitmask_settings & MASK_AUTHOR_SWAP) and len(parsed_vars["authors"]) >= 2:
        parsed_vars["authors"] = mutate_author_swap(parsed_vars["authors"])
        mutations_applied_log.append("author_swap")
    # does the aforementioned bitwise check but for title typo
    if (bitmask_settings & MASK_TITLE_TYPO) and parsed_vars["title"]:
        parsed_vars["title"] = introduce_typo(parsed_vars["title"])
        mutations_applied_log.append("title_typo")
    # does the aforementioned bitwise check but for year shift
    if (bitmask_settings & MASK_YEAR_SHIFT) and parsed_vars["year"]:
        parsed_vars["year"] = mutate_year_shift(parsed_vars["year"])
        mutations_applied_log.append("year_shift")
    # does the aforementioned bitwise check but for doi corruption
    if (bitmask_settings & MASK_DOI_CORRUPT) and parsed_vars["doi"]:
        parsed_vars["doi"] = parsed_vars["doi"][:-3] + "999"
        mutations_applied_log.append("doi_corrupt")

    # returns the values for the bitwise check thing that Ravi wanted, along with printing the relevant data in the
    # following order: the id of the citation, ama, apa, mla, nlm, and ris.
    return {
        "original_id": parsed_vars["id"],
        "mutation_bitmask_bin": f"0b{bitmask_settings:04b}",  # e.g. "0b0110"
        "mutation_bitmask_int": bitmask_settings,  # e.g. 6
        "mutations_applied": mutations_applied_log,
        "data": {
            "id": parsed_vars["id"],
            "ama": build_ama(parsed_vars),
            "apa": build_apa(parsed_vars),
            "mla": build_mla(parsed_vars),
            "nlm": build_nlm(parsed_vars),
            "ris": original_entry.get("ris")
        }
    }

# this is where the loop is stored. it begins by first generating the dictionary where it will be stored, then
# loops through all of the generations until we see a total of 2400 citations.
def generate_balanced_dataset(real_refs: list) -> list:
    final_output_database = []
    # the "pool" where the options for an error can be chosen from.
    single_bits_pool = [MASK_AUTHOR_SWAP, MASK_TITLE_TYPO, MASK_YEAR_SHIFT, MASK_DOI_CORRUPT]

    # 100 entries, 400 total citations (not including RIS)
    print("Processing Section 1/3: 100 Pristine Baselines...")
    for ref in real_refs:
        final_output_database.append(permute_reference(ref, bitmask_settings=MASK_REAL))
    # 200 entries, 800 total citations (not including RIS)
    print("Processing Section 2/3: 200 Single-Field Permutations...")
    for _ in range(2):
        for ref in real_refs:
            random_single_bit = random.choice(single_bits_pool)
            final_output_database.append(permute_reference(ref, bitmask_settings=random_single_bit))
    # 300 entries, 1200 total citations (not including RIS)
    print("Processing Section 3/3: 300 Multi-Field Permutations...")
    for _ in range(3):
        for ref in real_refs:
            # RNG selection of layout for 2 or 3 distinct bit-switches
            k_count = random.randint(2, 3)
            selected_bits = random.sample(single_bits_pool, k=k_count)
            # then this combines the selected single bits into a compound mask using bitwise OR gate
            compound_bitmask = 0
            for bit in selected_bits:
                compound_bitmask |= bit
            final_output_database.append(permute_reference(ref, bitmask_settings=compound_bitmask))
    return final_output_database # yippee now this exists :D


# "let's see if everything runs accordingly" section
if __name__ == "__main__":
    input_file = "references.json" # generated from Ravi's program
    output_file = "mutationcombinedoutput.json"
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            references_pool = json.load(f)
        print(f"[Success] Loaded {len(references_pool)} baseline source references.")
    except FileNotFoundError:
        print(f"Error: Could not locate '{input_file}' in your workspace directory.")
        exit()
    compiled_dataset = generate_balanced_dataset(references_pool)

    # gather database metrics using bitwise logic counters instead of strings (Ravi wanted this)
    real_count = 0
    single_field_count = 0
    multi_field_count = 0

    for entry in compiled_dataset:
        mask = entry["mutation_bitmask_int"]
        active_bits = bin(mask).count("1")
        #counter for the bits.
        if active_bits == 0:
            real_count += 1
        elif active_bits == 1:
            single_field_count += 1
        else:
            multi_field_count += 1

    print("\nCOMPILATION MATRIX REPORT")
    print(f"Total Structured Document Entries Saved: {len(compiled_dataset)}")
    print(f"  -> Section 1 (Real Baselines [0b0000]):        {real_count} entries")
    print(f"  -> Section 2 (Single-Bit Mutations [1 active]): {single_field_count} entries")
    print(f"  -> Section 3 (Multi-Bit Mutations [2+ active]): {multi_field_count} entries")
    print(" ")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(compiled_dataset, f, indent=2)

    print(f"\n The integration of the database has SUCCESSFULLY been generated and saved to '{output_file}'.")
