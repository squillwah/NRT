
# If we want to filter papers by journal, topic, etc. - use the esearch to grab paper IDs
# If we don't care, use the oa-servce to grab papers IDs in order of last updated in db (not the same as publication date)

# Use the citation exporter to create formal AMA, APA, MLA, & NLM references from PMCIDs.
# In addition to references, we can also grab RIS and NBIB expanded formats for additional metadata.

# Should we tell the chatbots which reference format the reference is "supposed" to be in? Do LLMs adhere to a format when "correcting" citations or generating them outright? 

import requests
import json
import xml.etree.ElementTree as ET
import time

# ! Note: none of these functions handle unexpected responses. They will throw errors with bad IDs, search terms, dates, etc.

# "When using this API programmatically, we request that you limit your application's rate to 3 requests per second and 
# do not make concurrent requests to this service, even at off-peak times. Any site (IP address) posting more than 3 requests 
# per second to the service will receive an error message. Use the tool and email parameters to identify the application making the request."
REQUEST_DELAY = .34
REQUEST_IDENTIFIER_TOOL = "reference_scraper"
REQUEST_IDENTIFIER_EMAIL = "DRE44769@pennwest.edu"
ENDPOINT_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ENDPOINT_OASERVICE = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
#ENDPOINT_CITATIONS = "https://pmc.ncbi.nlm.nih.gov/api/ctxp/v1/pubmed/"
ENDPOINT_CITATIONS = "https://pmc.ncbi.nlm.nih.gov/api/ctxp/v1/pmc/"
ENDPOINT_IDCONVERTER = "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"

def kindly_get(url, params):
    time.sleep(REQUEST_DELAY)
    return requests.get(url, params=({"tool":REQUEST_IDENTIFIER_TOOL, "email":REQUEST_IDENTIFIER_EMAIL} | params))

# Returns a list of JSON/dicts containing DOIs, PMCIDs and PMIDs for each given PMCID.
# ----
def all_ids(*pmcids):
    MAX_IDS = 200   # The API service allows for up to 200 IDs in a single request.
    id_lists = []
    if isinstance(pmcids, tuple) and len(pmcids) > MAX_IDS:
        id_lists = all_ids(*pmcids[MAX_IDS:])
        pmcids = pmcids[0:MAX_IDS]
    id_lists = kindly_get(ENDPOINT_IDCONVERTER, params={"format":"json", "ids":",".join(pmcids)}).json()["records"] + id_lists # Insert at head to maintain parallel order with arguments
    return id_lists

# Returns PMCIDs within OA subset corresponding to given search term.
# ----
def get_papers_filter(count, terms):
    # Max of 100,000 for one search request
    request = kindly_get(ENDPOINT_ESEARCH, params={"db":"pmc", "sort":"pubdate", "format":"json", "term":f"open_access[Filter]{terms}", "retmax":count})
    #return ["PMC"+ID for ID in request.json()["esearchresult"]["idlist"]]
    return request.json()["esearchresult"]["idlist"]

# Returns PMCIDs updated in OA database within date range (not the same as publication range).
# ----
def get_papers_range(count, start, end):
    # ! Only retrieves first 1000 at maximum. Will need to use resumptiontoken for more.
    request = kindly_get(ENDPOINT_OASERVICE, params={"from":start, "until":end})
    xml = ET.fromstring(request.text)
    return [record.attrib["id"] for record in xml.find("records").findall("record")[:count]]

# Returns a JSON/dict of nested dicts containing all formal citation formats for each given paper.
# ! Note: needs PMIDs, not PMCIDS. Set the flag to attempt auto translation via all_ids().
# ----
def extract_reference_formats(*pmcids, translate_IDs=False):
    #if translate_IDs: pmids = [ID["pmid"] for ID in all_ids(*pmids)]
    # ! Requests may have some maximum, documentation is unclear.
    RIS_DELIM = "ER - \r\n"
    refs = kindly_get(ENDPOINT_CITATIONS, params={"format":"citation", "id":pmcids}).json() # JSON of AMA, APA, MLA, & NLM for each PMCID
    riss = [ris+RIS_DELIM for ris in kindly_get(ENDPOINT_CITATIONS, params={"format":"ris", "id":pmcids}).text.split(RIS_DELIM)] # List of RIS metadata text
    #with open("fart.txt", "w") as fart: fart.write(kindly_get(ENDPOINT_CITATIONS, params={"format":"ris", "id":pmcids}).text)
    for paper_refs, paper_ris in zip(refs, riss): paper_refs["ris"] = paper_ris # Include RIS as entry within refs JSON
    return refs

# @todo: Something to parse the RIS metadata. If using that is something we're going to include as an experiment.

if __name__ == "__main__":
    print("Searching papers.")
    paper_pmcids = get_papers_filter(100, "Nature[Journal]") # Could do multiple journals in a search, or grab an exact amount from each in seperate calls for equal ratios. And more.
    print(paper_pmcids)

    print("Mapping IDs")
    #paper_IDs = all_ids(*paper_pmcids)
    #print(json.dumps(paper_IDs, indent=2))

    print("Fetching references")           # or (*paper_pmcids, translate_IDs=True)
    #paper_references = extract_reference_formats([ID["pmid"] for ID in paper_IDs])
    paper_references = extract_reference_formats(*paper_pmcids)
    #print(json.dumps(paper_references, indent=2))

    print("Writing to file")
    try:
        with open("references2.json", "x") as file: json.dump(paper_references, file, indent=2)
        print("Saved to 'references.json'")
    except FileExistsError:
        if input("! 'references.json' already exists, overwrite? [y/n]: ").strip().lower() == "y":
            with open("references.json", "w") as file: json.dump(paper_references, file, indent=2)
            print("Saved to 'references.json'")
        else: print("Write cancelled")



