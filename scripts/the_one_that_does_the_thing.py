from pmc_grabber import grab_articles
from llm_multichatter import Gemini


articles = grab_articles("Nature", 10)
parsed_refs = []

for ID in articles:
    passages = articles[ID]["FULLTEXT"][0]["documents"][0]["passages"]

    # Parse all references directly into clean dicts
    for p in passages:
        if p["infons"].get("section_type") == "REF" and p["infons"].get("type") == "ref":
            info = p["infons"]
            parsed_refs.append({
                "title": p["text"],
                "doi": info.get("pub-id_doi"),
                "pmid": info.get("pub-id_pmid"),
                "year": info.get("year"),
                "journal": info.get("source"),
                "volume": info.get("volume"),
                "fpage": info.get("fpage"),
                "lpage": info.get("lpage"),
                "citation": info.get("citation-alternatives")
            })

header_prompt = "DO NOT USE THE INTERNET. Analyze this citation given and tell me if it is real or not. Did you use the internet? What percentage confidence do you think this citation is real? Then explain how you came up with that number?"

response = Gemini.send_prompt("gemma-4-26b-a4b-it", header_prompt + parsed_refs[0]["citation"])
print("\nThe response is: \n\n", Gemini.parse_response(response))