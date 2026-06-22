
import requests
import json
import xml.etree.ElementTree as ET
import time

# Functions to get article IDs and reference data using PMC APIs.
# ! Note: no error handling. Unexpected responses (from bad IDs, terms, dates, etc.) will throw exceptions.

# "When using this API programmatically, we request that you limit your application's rate to 3 requests per second do not make concurrent requests to this service, even at off-peak times." 
# "Use the tool and email parameters to identify the application making the request."
REQUEST_DELAY = .34
REQUEST_IDENTIFIER_TOOL = "reference_scraper"
REQUEST_IDENTIFIER_EMAIL = "DRE44769@pennwest.edu"

ENDPOINT_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ENDPOINT_OASERVICE = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
ENDPOINT_CITATIONS = "https://pmc.ncbi.nlm.nih.gov/api/ctxp/v1/pmc/"    #v1/pubmed/"    Pubmed database does not understand all PMCIDs.
ENDPOINT_IDCONVERTER = "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"

# Make requests compliant with service guidelines.
def kindly_get(url, params):
    time.sleep(REQUEST_DELAY)
    return requests.get(url, params=({"tool":REQUEST_IDENTIFIER_TOOL, "email":REQUEST_IDENTIFIER_EMAIL} | params))

# Returns a list of JSON/dicts containing DOIs, PMCIDs and PMIDs for each given PMCID.
# (no longer used, search returns PMCID which is all we need)  
def all_ids(*pmcids):
    MAX_IDS = 200   # The API service allows for up to 200 IDs in a single request.
    id_lists = []
    if isinstance(pmcids, tuple) and len(pmcids) > MAX_IDS:
        id_lists = all_ids(*pmcids[MAX_IDS:])
        pmcids = pmcids[0:MAX_IDS]
    id_lists = kindly_get(ENDPOINT_IDCONVERTER, params={"format":"json", "ids":",".join(pmcids)}).json()["records"] + id_lists # Insert at head to maintain parallel order with arguments
    return id_lists

# Returns PMCIDs within OA subset corresponding to given search term.
def get_papers_filter(count, terms):
    # Max of 100,000 for one search request
    EXCLUDE = ("articletypeexpressionofconcern", "articletypecorrection", "articletyperetraction")
    request = kindly_get(ENDPOINT_ESEARCH, params={
        "db":"pmc", "sort":"pubdate", "format":"json",
        "term":f"open_access[Filter]{terms} NOT ({" OR ".join(EXCLUDE)})",
        "retmax":count})
    #return ["PMC"+ID for ID in request.json()["esearchresult"]["idlist"]]
    return request.json()["esearchresult"]["idlist"]

# Returns PMCIDs updated in OA database within date range (not the same as publication range).
# (not used, filter is just better)
def get_papers_range(count, start, end):
    # ! Only retrieves first 1000 at maximum. Will need to use resumptiontoken for more.
    request = kindly_get(ENDPOINT_OASERVICE, params={"from":start, "until":end})
    xml = ET.fromstring(request.text)
    return [record.attrib["id"] for record in xml.find("records").findall("record")[:count]]

def get_ref(*pmcids):
    return kindly_get(ENDPOINT_CITATIONS, params={"format":"citation", "id":pmcids}).json() # JSON of AMA, APA, MLA, & NLM for each PMCID
def get_ris(*pmcids):
    RIS_DELIM = "ER  - \r\n"
    return [ris+RIS_DELIM for ris in kindly_get(ENDPOINT_CITATIONS, params={"format":"ris", "id":pmcids}).text.split(RIS_DELIM)[:-1]] # List of RIS metadata text. ! Slice off last element, for split leaves it empty (due to trailing /r/n)

# Returns a JSON/dict of nested dicts containing all formal citation formats for each given paper.
# (no longer used, baking citations ourselves only necessitates RIS)
def extract_reference_formats(*pmcids): #(*pmids, translate_IDs=False):
    #if translate_IDs: pmids = [ID["pmid"] for ID in all_ids(*pmids)]
    # ! Requests may have some maximum, documentation is unclear.
    refs = get_ref(pmcids)
    riss = get_ris(pmcids)
    for paper_refs, paper_ris in zip(refs, riss): paper_refs["ris"] = paper_ris # Include RIS as entry within refs JSON
    return refs

# Test fetch of 100 latest Nature articles. 
if __name__ == "__main__":
    print("Searching papers.")
    paper_pmcids = get_papers_filter(100, "Nature[Journal]")
    print(paper_pmcids)

    # Made redundant by change to PMC db from PubMed db in reference API
    # print("Mapping IDs")
    # paper_IDs = all_ids(*paper_pmcids)
    # paper_references = extract_reference_formats([ID["pmid"] for ID in paper_IDs])

    print("Fetching references")
    paper_references = extract_reference_formats(*paper_pmcids)

    print("Writing to file")
    try:
        with open("references2.json", "x") as file: json.dump(paper_references, file, indent=2)
        print("Saved to 'references.json'")
    except FileExistsError:
        if input("! 'references.json' already exists, overwrite? [y/n]: ").strip().lower() == "y":
            with open("references.json", "w") as file: json.dump(paper_references, file, indent=2)
            print("Saved to 'references.json'")
        else: print("Write cancelled")



