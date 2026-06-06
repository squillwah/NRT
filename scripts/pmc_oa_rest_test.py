import requests
import json
#import xml.etree.ElementTree as ET

BASE_URLS = {"UTIL":"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",                 # PMC Database Search
            "OA":"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi",                # Open Access Subset DB
            "OAI":"https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh/",                     # OA Subset Metadata DB
            "BIOC":"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi", # OA Subset (BioC Format) DB
            "CITE":"https://pmc.ncbi.nlm.nih.gov/api/ctxp/",                         # Citation Exporter
            "ID":"https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"}       # PMC ID Converter (PMCID, PMID, DOI, ...)

DB_FETCH_URL = BASE_URLS["UTIL"]+"efetch.fcgi"
DB_SEARCH_URL = BASE_URLS["UTIL"]+"esearch.fcgi"


#payload = {"db":"pmc", "term":"cancer"} # Pretty sure pmc means all OA papers, but not sure.
#response = requests.get(DB_SEARCH_URL, params=payload)
#print(response.url)
#print(response.text)
#print(response.headers)
#print("\n\n\n", "\n".join(vars(response)), "\n\n\n")
#print(response.content)

article = None
article_id = 0
database_uid = 0
payload = None
response = None
response_data = None

# Search PMC database for papers on "cancer"
payload = {"db":"pmc",
           "sort":"pub date",
           "format":"json",     # Some other params could probably go here, filtering etc. Does PMC contain only OA papers?
           "term":"Cancer AND open_access[filter] AND free_full_text[filter]"}
response = requests.get(DB_SEARCH_URL, params=payload)
if (response.status_code != 200):
    print(f"Failed to GET {response.url} with code {response.status_code}")
    quit()
response_data = response.json()
database_uid = response_data["esearchresult"]["idlist"][1] # First result
print(f"Found article in PMC database with UID '{database_uid}'")
print(response.url)

# Fetch article info from database, map UID to PMCID        * This step might be completely unnecessary, not sure.
payload = {"db":"pmc",
           "id":database_uid}
response = requests.get(DB_FETCH_URL, params=payload)
if (response.status_code != 200):
    print(f"Failed to GET {response.url} with code {response.status_code}")
    quit()
response_data = response.text # XML parsing 
xml_pmcid_delims = ('<article-id pub-id-type="pmcid">', '</article-id>')
xml_pmcid_indices = [response_data.find(xml_pmcid_delims[0]), response_data.find(xml_pmcid_delims[1])]
xml_pmcid_indices[0] = xml_pmcid_indices[0] + len(xml_pmcid_delims[0])
article_id = response_data[xml_pmcid_indices[0]:xml_pmcid_indices[1]]
print(f"Mapped database UID '{database_uid}' to PMCID '{article_id}'")
print(response.url)

# Get DoiC formatted copy of article, as unicode JSON.
response = requests.get(f"{BASE_URLS["BIOC"]}/BioC_json/{article_id}/unicode")
if (response.status_code != 200):
    print(f"Failed to GET {response.url} with code {response.status_code}")
    quit()
print(response.url)
print(response.content)
response_data = response.json()
print(json.dumps(response_data, indent=4))
    #article_id = response_data[3][0].text # idList is the fourth child of XML root.

# Keep getting not found errors with the DoiC database. 
# I think it just doesn't have all the papers indexed in that format, and I can't find a way to restrict the search. 
# Not like that really matters tho, cause it's only testing.


