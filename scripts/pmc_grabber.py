
# Downloads the 10 latest OA articles from Nature (in PDF format?)
# Extracts citations in both raw text and JSON representations. (not really)

# Searches PMC for articles, downloads BioC JSON full test and PMC OA database file info XML

# ! There is no error handling in any of this. It will break if something goes wrong.

import requests
import json
import xml.etree.ElementTree as ET
import time

API = {"SEARCH":"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
       "ACCESS":"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi",
       "BIOC":"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi"}

REQUEST_DELAY = .35 # Delay between requests, to avoid timeouts / getting blocked

# To remove clutter with payload/request configuring stuff. 
# Use the tailored rsets to set the request accordingly, then get the response with rget.
class RequestState:
    def __init__(self):
        self.url = ""
        self.payload = {}
def rget(rstate):
    time.sleep(REQUEST_DELAY)
    return requests.get(rstate.url, params=rstate.payload)

# For grabbing result set response of paper ID from PMC OA
# https://pmc.ncbi.nlm.nih.gov/tools/oa-service/
def rset_paper_request(rstate, identifier):
    rstate.url = API["ACCESS"]
    rstate.payload = {"id":identifier}
# For grabbing 20 most recent OA paper IDs published in journal
# https://www.ncbi.nlm.nih.gov/books/NBK25501/
def rset_search_request(rstate, journal, num_articles):
    rstate.url = API["SEARCH"]
    rstate.payload = {"db":"pmc", "sort":"pubdate", "format":"json",
                      "term":f"{journal}[Journal]open_access[Filter]",
                      "retmax":num_articles}
# For grabbing the JSON BIOC formatted fulltext of the given OA article
# https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PMC/
def rset_bioc_request(rstate, article):
    rstate.url = f"{API["BIOC"]}/BioC_json/{article}/unicode"
    rstate.payload = {}

# Return num_articles latest articles from journal
# Data format: dict(pmcid:dict(pmcinfo:xml, fulltext:json))
def grab_articles(journal, num_articles):
    rs = RequestState()
    response = None
    articles = {}

    # Grab PMC IDs, create key entries in map
    rset_search_request(rs, journal, num_articles)
    response = rget(rs)
    for ID in response.json()["esearchresult"]["idlist"]:
        ID = "PMC"+ID # Prefix each ID with "PMC" to make PMCIDs.
        articles[ID] = {"PMCINFO":None, "FULLTEXT":None}

    # Fetch PMC OA info and JSON fulltext
    for ID in articles:
        rset_paper_request(rs, ID)
        response = rget(rs)
        articles[ID]["PMCINFO"] = ET.ElementTree(ET.fromstring(response.text)) # Structure as XML etree

        rset_bioc_request(rs, ID)
        response = rget(rs)
        articles[ID]["FULLTEXT"] = response.json() # Structure as JSON object

    return articles

def write_articles_to_file(articles, target_dir):
    for ID in articles:
        with open(f"{target_dir}/{ID}_info.xml", "wb") as file:
            ET.indent(articles[ID]["PMCINFO"], space="  ") # Indent for human xml formatting.
            articles[ID]["PMCINFO"].write(file, encoding="utf-8", xml_declaration=True)
        with open(f"{target_dir}/{ID}.json", "w") as file:
            json.dump(articles[ID]["FULLTEXT"], file, indent=2)

#articles = {"PMCID":[None]*ARTICLE_COUNT,     # The article ID
#            "PMCINFO":[None]*ARTICLE_COUNT,   # Info about article in PMC OA FTP database (XML ElementTree)
#            "FULLTEXT":[None]*ARTICLE_COUNT}  # Full text of the article, in BioC formatted JSON


if __name__ == "__main__":
    JOURNAL = "Nature"
    ARTICLE_COUNT = 10
    TARGET_DIR = "./pmc_grabber/"

    print("Grabbing articles... ")
    articles = grab_articles(JOURNAL, ARTICLE_COUNT)
    for ID in articles.keys(): print(f"- {ID}")
    print("Writing to file... ")
    write_articles_to_file(articles, TARGET_DIR)
    for ID in articles.keys(): print(f"- {TARGET_DIR}/{ID}.json \n- {TARGET_DIR}/{ID}_info.xml")

"""
# --------
# Get article ID list
# --------
rset_search_request(rs, JOURNAL, ARTICLE_COUNT)
response = rget(rs)
articles["PMCID"] = ["PMC"+ID for ID in response.json()["esearchresult"]["idlist"]] # Prefix each ID with "PMC" to make PMCIDs.
print(f"{ARTICLE_COUNT} latest OA articles in {JOURNAL}: {"\n- ".join(articles["PMCID"])}")

# --------
# Grab article JSON and OA file info 
# --------
for i in range(0, ARTICLE_COUNT):
    print(f"Grabbing {articles["PMCID"][i]}...")

    # OA file info XML 
    rset_paper_request(rs, articles["PMCID"][i])
    response = rget(rs)
    articles["PMCINFO"][i] = ET.ElementTree(ET.fromstring(response.text))

    # Full text BioC JSON
    rset_bioc_request(rs, articles["PMCID"][i])
    response = rget(rs)
    articles["FULLTEXT"][i] = response.json()

# --------
# Parse citations ...
# --------

# --------
# Write to file
# --------

for i in range(0, ARTICLE_COUNT):
    print(f"Writing {articles["PMCID"][i]} to file...")

    with open(f"{TARGET_DIR}/{articles["PMCID"][i]}_info.xml", "wb") as file:
        ET.indent(articles["PMCINFO"][i], space="  ") # Indent for human xml formatting.
        articles["PMCINFO"][i].write(file, encoding="utf-8", xml_declaration=True)
    with open(f"{TARGET_DIR}/{articles["PMCID"][i]}.json", "w") as file:
        json.dump(articles["FULLTEXT"][i], file, indent=2)
"""
