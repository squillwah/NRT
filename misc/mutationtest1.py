# loads all the packages that would be used. .json for how the file will be saved, random for certain portions of
# parsible text within the citation, and then copying dictionaries.
import json
import random
import copy

# okay so for this part, taking Ravi's references.json file and all 600 will be generated. for this specific part,
# we take the RIS that was attached after each citation and go from there. this is done through primarily analyzing
# each instance of where authors / title / year / doi / other lines starts and documenting it
def parse_ris(ris_string: str) -> dict:
    ris_data = {
        "authors": [],
        "title": "",
        "year": "",
        "doi": "",
        "other_lines": []
    }
    for line in ris_string.splitlines():
        if line.startswith("AU  - "):
            ris_data["authors"].append(line[6:].strip())
        elif line.startswith("T1  - "):
            ris_data["title"] = line[6:].strip()
        elif line.startswith("Y1  - "):
            ris_data["year"] = line[6:].strip()
        elif line.startswith("DO  - "):
            ris_data["doi"] = line[6:].strip()
        elif line.strip():
            ris_data["other_lines"].append(line)
    return ris_data

# the RIS is rebuilt in this section. remember that above they were separated, this appends them together with the
# relevant dashes that would then structure it all after showing the relevant data and whatnot
def rebuild_ris(ris_data: dict) -> str:
    lines = ["TY  - JOUR"]
    for author in ris_data["authors"]:
        lines.append(f"AU  - {author}")
    if ris_data["title"]:
        lines.append(f"T1  - {ris_data['title']}")
    if ris_data["year"]:
        lines.append(f"Y1  - {ris_data['year']}")
    if ris_data["doi"]:
        lines.append(f"DO  - {ris_data['doi']}")
    for line in ris_data["other_lines"]:
        if not any(line.startswith(prefix) for prefix in ["TY  -", "AU  -", "T1  -", "Y1  -", "DO  -"]):
            lines.append(line)
    # joins them together
    return "\r\n".join(lines) + "\r\n"



# the part of the code where "shit" is supposed to hit the fan. here is where the typos are defined, ensuring that
# the title receives a switch in two letters, typically after two words, where their positions are swapped
def introduce_typo(text: str) -> str:
    if len(text) < 2:
        return text
    idx = random.randint(0, len(text) - 2)
    text_list = list(text)
    text_list[idx], text_list[idx + 1] = text_list[idx + 1], text_list[idx]
    return "".join(text_list)
# simply switches the authors positions from 0 to 1, and 1 to 0
def mutate_author_swap(authors: list) -> list:
    if len(authors) >= 2:
        new_authors = copy.deepcopy(authors)
        new_authors[0], new_authors[1] = new_authors[1], new_authors[0]
        return new_authors
    return authors
# chooses a random year variation (1-2 years before original publishing, 1-2 years after) and outputs it
def mutate_year_shift(year_str: str) -> str:
    parts = year_str.split('/')
    try:
        altered_year = int(parts[0]) + random.choice([-2, -1, 1, 2])
        parts[0] = str(altered_year)
        return "/".join(parts)
    except ValueError:
        return year_str



# this portion of the code reads the ris data and then organizes it into their own dictionary slots (or parsed_ris).
def permute_reference(original_entry: dict, settings: list) -> dict:
    ris_content = original_entry.get("ris", "")
    parsed_ris = parse_ris(ris_content)

    mutations_recorded = [] # the place where the animatronics get quirky at night (stores the errors for that
    # single iteration)
    # if loop that just looks through number of authors, checks if a title exists, moves the year around, yada
    # yada just so that way some error can appear. 
    for setting in settings:
        if setting == "author_swap" and parsed_ris["authors"]:
            parsed_ris["authors"] = mutate_author_swap(parsed_ris["authors"])
            mutations_recorded.append("author_swap")
        elif setting == "title_typo" and parsed_ris["title"]:
            parsed_ris["title"] = introduce_typo(parsed_ris["title"])
            mutations_recorded.append("title_typo")
        elif setting == "year_shift" and parsed_ris["year"]:
            parsed_ris["year"] = mutate_year_shift(parsed_ris["year"])
            mutations_recorded.append("year_shift")
        elif setting == "doi_corrupt" and parsed_ris["doi"]:
            parsed_ris["doi"] = parsed_ris["doi"][:-3] + "999"
            mutations_recorded.append("doi_corrupt")

    if len(mutations_recorded) == 0:
        classification = "real" # legitness
    elif len(mutations_recorded) == 1:
        classification = "single-field" # simulation of AI making silly mistake
    else:
        classification = "multi-field" # simulation of AI being stupid

    mutated_entry = copy.deepcopy(original_entry)
    mutated_entry["ris"] = rebuild_ris(parsed_ris)
    # portion of code that just outputs data prior to the existence of RIS portion of permutation / generation
    return {
        "original_id": original_entry.get("id"),
        "classification": classification,
        "mutations_applied": mutations_recorded,
        "data": mutated_entry
    }



# this portion generates the mutations that will then be used later on.
# each subsection divides it into either 100 sources of no mutations, 200 with mutations, and 300 with multi-mutations.
def generate_dataset(real_refs: list) -> list:
    generated_database = []
    available_mutations = ["author_swap", "title_typo", "year_shift", "doi_corrupt"]

    # part 1) no changes whatsoever.
    print("Generating 100 true baseline references...")
    for ref in real_refs:
        generated_database.append(permute_reference(ref, settings=[]))
    # part 2) single-field permutations, done with 100 references and 2 passes
    print("Generating ~200 single-field mutation references...")
    for pass_num in range(2):
        for ref in real_refs:
            chosen_mutation = [random.choice(available_mutations)]
            generated_database.append(permute_reference(ref, settings=chosen_mutation))
    # part 3) multi-field permutations, done with 100 references and 3 passes
    print("Generating ~300 multi-field mutation references...")
    for pass_num in range(3):
        for ref in real_refs:
            # rng of 2-3 to choose how many permutations would be present
            num_mutations = random.randint(2, 3)
            chosen_mutations = random.sample(available_mutations, k=num_mutations)
            generated_database.append(permute_reference(ref, settings=chosen_mutations))

    return generated_database



if __name__ == "__main__":
    # loads the original references.json and the length of it.
    try:
        with open("references.json", "r", encoding="utf-8") as f:
            real_refs = json.load(f)
        print(f"Successfully loaded {len(real_refs)} raw citations.")
        # in the off-chance that shit doesn't load, and we create a larger headache for ourselves
    except FileNotFoundError:
        print("Error: Could not find 'references.json'.")
        exit()

    # generates the final dataset and then counts the number of them in said document
    final_dataset = generate_dataset(real_refs)
    counts = {"real": 0, "single-field": 0, "multi-field": 0}
    for item in final_dataset:
        counts[item["classification"]] += 1

    # just some simple print statements for this, shows the total that were generated
    # do note: because of how gacha luck works, sometimes we will get "author_swap" on a paper written by
    # one person and hence we get a number greater than 100 for the true baseline.
    print("\n--- GENERATION REPORT ---")
    print(f"Total Rows Generated: {len(final_dataset)}")
    print(f"  -> Real/True Baseline: {counts['real']}")
    print(f"  -> Single-Field Edits: {counts['single-field']}")
    print(f"  -> Multi-Field Edits:  {counts['multi-field']}")

    # saves the .json file with the new permuted data
    output_filename = "permuted_dataset.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, indent=2)
    print(f"\n[Success] Final dataset compiled and saved to '{output_filename}'!")