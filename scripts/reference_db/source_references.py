
# If we want to filter papers by journal, topic, etc. - use the esearch to grab paper IDs
# If we don't care, use the oa-servce to grab papers IDs in order of last updated in db (not the same as publication date)

# Use the citation exporter to create formal AMA, APA, MLA, & NLM references from PMCIDs.
# In addition to references, we can also grab RIS and NBIB expanded formats for additional metadata.

# Should we tell the chatbots which reference format the reference is "supposed" to be in? Do LLMs adhere to a format when "correcting" citations or generating them outright? 

import requests
import json
import xml.etree.ElementTree as ET
import time

# "When using this API programmatically, we request that you limit your application's rate to 3 requests per second and do not make concurrent requests to this service, even at off-peak times. Any site (IP address) posting more than 3 requests per second to the service will receive an error message. Use the tool and email parameters to identify the application making the request."
REQUEST_DELAY = .34
REQUEST_IDENTIFIER_TOOL = "reference_scraper"
REQUEST_IDENTIFIER_EMAIL = "DRE44769@pennwest.edu"
ENDPOINT_ESEARCH = ""
ENDPOINT_OASERVICE = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
ENDPOINT_CITATIONS = "https://pmc.ncbi.nlm.nih.gov/api/ctxp/v1/pubmed/"
ENDPOINT_IDCONVERTER = "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"

def kindly_get(url, params):
    time.sleep(REQUEST_DELAY)
    return requests.get(url, params=({"tool":REQUEST_IDENTIFIER_TOOL, "email":REQUEST_IDENTIFIER_EMAIL} | params))

# ! Note: none of these handle unexpected responses. They will throw errors.

# Returns a list of JSON/dicts containing DOIs, PMCIDs and PMIDs for each given PMCID.
def all_ids(*pmcids):
    MAX_IDS = 200   # The API service allows for up to 200 IDs in a single request.
    id_lists = []
    if isinstance(pmcids, tuple) and len(pmcids) > MAX_IDS:
        id_lists = all_ids(*pmcids[MAX_IDS:])
        pmcids = pmcids[0:MAX_IDS]
    id_lists = kindly_get(ENDPOINT_IDCONVERTER, params={"format":"json", "ids":",".join(pmcids)}).json()["records"] + id_lists # Insert at head to maintain parallel order with arguments
    return id_lists

# Returns a # of PMCIDs within OA subset corresponding to given search term.
def get_papers_filter(count, terms): pass

# Returns a # of PMCIDs updated in OA database within date range (not the same as publication range).
def get_papers_range(count, start, end):
    # ! rn only gets first 1000 max, will need to use resumptiontoken for more later
    request = kindly_get(ENDPOINT_OASERVICE, params={"from":start, "until":end})
    print(request.url)
    xml = ET.fromstring(request.text)
    return [record.attrib["id"] for record in xml.find("records").findall("record")[:count]]

# Returns a JSON/dict of nested dicts containing all formal citation formats for each given paper.
def extract_reference_formats(*pmids):
    # May have some maximum, it is unclear.
    refs = kindly_get(ENDPOINT_CITATIONS, params={"format":"citation", "id":pmids}).json() #JSON of AMA, APA, MLA, & NLM for each PMCID
    return refs

#    (None) * len(pmcids)
#    for index, ID in enumerate(pmcids):
#        refs[index] = {"FORMAL": 
#

#print(json.dumps(all_ids("PMC1193645", "PMC1134901"), indent=2))
#print(json.dumps(all_ids("PMC1134901", "PMC1193645"), indent=2))

paper_IDs = all_ids(*get_papers_range(2, "2026-01-01", "2026-04-01"))
paper_refs = extract_reference_formats(*[ID["pmid"] for ID in paper_IDs])
print(json.dumps(paper_IDs, indent=2))
print(json.dumps(paper_refs, indent=2))



