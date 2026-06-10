
# Downloads the 10 latest OA articles from Nature (in PDF format?)
# Extracts citations in both raw text and JSON representations. (not really)

# Searches PMC for articles, downloads BioC JSON full test and PMC OA database file info XML

import requests
import json
import xml.etree.ElementTree as ET

JOURNAL = "Nature"
ARTICLES = 10
TARGET_DIR = "./pmc_grabber/"

API = {"SEARCH":"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
       "ACCESS":"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi",
       "BIOC":"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi"}

# To remove clutter with payload/request configuring stuff. 
# Use the tailored rsets to set the request accordingly, then get the response with rget.
class RequestState:
    def __init__(self):
        self.url = ""
        self.payload = {}
def rget(rstate): return requests.get(rstate.url, params=rstate.payload)

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

rs = RequestState()
response = None
article_list = None

# --------
# Get article ID list
# --------
rset_search_request(rs, JOURNAL, ARTICLES)
response = rget(rs)
article_list = ["PMC"+ID for ID in response.json()["esearchresult"]["idlist"]] # Prefix each ID with "PMC" to make PMCIDs.
print(f"{ARTICLES} latest OA articles in {JOURNAL}: {"\n- ".join(article_list)}")

# --------
# Grab article JSON and OA file info
# --------
for article in article_list:
    # OA file info XML 
    rset_paper_request(rs, article)
    response = rget(rs)
    info_xml = ET.ElementTree(ET.fromstring(response.text))
    ET.indent(info_xml, space="  ") # Human formatting in file.
    # Full text BioC JSON
    rset_bioc_request(rs, article)
    response = rget(rs)
    bioc_json = response.json()
    # Write to file
    with open(f"{TARGET_DIR}/{article}_info.xml", "wb") as file:
        info_xml.write(file, encoding="utf-8", xml_declaration=True)
    with open(f"{TARGET_DIR}/{article}.json", "w") as file:
        json.dump(bioc_json, file, indent=2)

# --------
# Parse citations ...
# --------

