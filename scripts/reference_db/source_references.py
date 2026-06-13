
# If we want to filter papers by journal, topic, etc. - use the esearch to grab paper IDs
# If we don't care, use the oa-servce to grab papers IDs in order of db acquisition

# Use the citation exporter to create formal AMA, APA, MLA, & NLM references from PMCIDs.
# In addition to references, we can also grab RIS and NBIB expanded formats for additional metadata.

# Should we tell the chatbots which reference format the reference is "supposed" to be in? Do LLMs adhere to a format when "correcting" citations or generating them outright? 

import requests
import json
import time



# "When using this API programmatically, we request that you limit your application's rate to 3 requests per second and do not make concurrent requests to this service, even at off-peak times. Any site (IP address) posting more than 3 requests per second to the service will receive an error message. Use the tool and email parameters to identify the application making the request."
REQUEST_DELAY = .34
REQUEST_IDENTIFIER_TOOL = "reference_scraper"
REQUEST_IDENTIFIER_EMAIL = "DRE44769@pennwest.edu"
ENDPOINT_ESEARCH = ""
ENDPOINT_OASERVICE = ""
ENDPOINT_CITATIONS = ""
ENDPOINT_IDCONVERTER = "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"

def kind_get(url, params):
    time.sleep(REQUEST_DELAY)
    return requests.get(url, params=({"tool":REQUEST_IDENTIFIER_TOOL, "email":REQUEST_IDENTIFIER_EMAIL} | params))

# Returns a list of dicts / JSON containing DOI, PMCID and PMID for each given PMCID
def all_ids(*pmcids):
    MAX_IDS = 200 # The API service allows for up to 200 IDs in a single request.
    id_lists = []
    #print(pmcids)
    if isinstance(pmcids, tuple) and len(pmcids) > MAX_IDS: #and (splits := len(pmcids)) // MAX_IDS > 0:
        id_lists = all_ids(*pmcids[MAX_IDS:])
        pmcids = pmcids[0:MAX_IDS]
    #print(id_lists)
    #response = requests.get(ENDPOINT_IDCONVERTER, params={"format":"json", "tool":REQUEST_IDENTIFIER_TOOL, "email":REQUEST_IDENTIFIER_EMAIL, "ids":",".join(pmcids)})
    #print(response.text)
    #id_lists = requests.get(ENDPOINT_IDCONVERTER, params={"format":"json",
    #                                                      "tool":REQUEST_IDENTIFIER_TOOL,
    #                                                      "email":REQUEST_IDENTIFIER_EMAIL,
    #                                                      "ids":",".join(pmcids)}).json()["records"] + id_lists # Insert at head to maintain parallel order with arguments
    #id_lists = response.json()["records"] + id_lists
    #print(id_lists)
    # ! note: no handling here for unexpected responses, will throw errors
    id_lists = kind_get(ENDPOINT_IDCONVERTER, params={"format":"json", "ids":",".join(pmcids)}).json()["records"] + id_lists # Insert at head to maintain parallel order with arguments
    return id_lists

def get_papers_filter(count, terms): pass

def get_papers_range(count, start, end): pass

def extract_reference_formats(*pmcids):
    refs = requests.get(ENDPOINT_CITATIONS, params={"format":"citation", "id":pmcids}) #JSON of AMA, APA, MLA, & NLM for each PMCID

#    (None) * len(pmcids)
#    for index, ID in enumerate(pmcids):
#        refs[index] = {"FORMAL": 
#

print(json.dumps(all_ids("PMC1193645", "PMC1134901"), indent=2))

print(json.dumps(all_ids("PMC1134901", "PMC1193645"), indent=2))
