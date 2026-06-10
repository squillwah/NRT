import requests
import json
#import xml.etree.ElementTree as ET     use this over helper for more complex stuff with xml 
#from ftplib import FTP
import urllib.request

# API base URLs
PMC = {"OA":  "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi",              # Open Access Subset DB
       "OAI": "https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh/",                    # OA Subset Metadata DB
       "BIOC":"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi", # OA Subset (BioC Format) DB
       "CITE":"https://pmc.ncbi.nlm.nih.gov/api/ctxp/",                         # Citation Exporter
       "ID":  "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"}     # PMC ID Converter (PMCID, PMID, DOI, ...)

EUTIL = {"SEARCH":"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",     # PMC Database Search
         "FETCH":"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"}

# Helpers
def fail_check(condition, msg):
    if condition:
        print(msg)
        quit()

def xml_extract_first(delims, xml):
    value = None
    value_start = xml.find(delims[0]) + len(delims[0])
    value_end = xml.find(delims[1], value_start)
    if value_end > value_start and value_start >= len(delims[0]): value = xml[value_start:value_end]
    return value

def download_pmc_ftp(url, filename):
    insert_deprecated = url.find("pmc/")+4  # PMC moved all rearranged their FTP files into a "/deprecated/" subfolder. Without updating the database URLs :)
    url = url[0:insert_deprecated]+"deprecated/"+url[insert_deprecated:]
    urllib.request.urlretrieve(url, filename)

def parse_oa_file_url(file_type, article_info_xml):
    url = xml_extract_first((f"<link format=\"{file_type}\"", "/>"), response.text)
    if url != None: url = url[url.find("href=")+5:].strip()[1:-1]
    return url

search_term = str(input("Enter search term: "))
print(f"Searching PMC database for OA papers on {search_term}...")

article = None
article_id = 0
database_uid = 0
payload = None
response = None
response_data = None

# Search PMC database for papers on "cancer"
print("\n Searching PMC")
#payload = {"db":"pmc", "sort":"pub date", "format":"json", "term":f"{search_term} AND open_access[filter]"} # Some other params could probably go here, filtering etc. Does PMC contain non OA papers or is that only PubMed?
payload = {"db":"pmc", "sort":"relevance", "format":"json", "term":search_term} # filter=collections.open_access&schema=all
response = requests.get(EUTIL["SEARCH"], params=payload)
fail_check((response.status_code != 200), f"! Failed to GET {response.url} with code {response.status_code}")
response_data = response.json()
fail_check((len(response_data["esearchresult"]["idlist"]) == 0), "! No articles found")
database_uid = response_data["esearchresult"]["idlist"][0] # First result
print(response.url)
print(f"Selecting article in PMC database with UID '{database_uid}' out of querried list: {response_data["esearchresult"]["idlist"]}")

# Fetch article info from database, map UID to PMCID        * This step might be completely unnecessary, not sure (is the PMCID always PMC+UID?)
print("\n Mapping UID to PMCID")
payload = {"db":"pmc", "id":database_uid}
response = requests.get(EUTIL["FETCH"], params=payload)
fail_check((response.status_code != 200), f"! Failed to GET {response.url} with code {response.status_code}")
response_data = response.text
article_id = xml_extract_first(('<article-id pub-id-type="pmcid">', '</article-id>'), response_data) # Parse PMCID from XML text
print(response.url)
print(f"Mapped database UID '{database_uid}' to PMCID '{article_id}'")

# Get DoiC formatted copy of article, as unicode JSON.
print("\n Requesting DoiC JSON")
response = requests.get(f"{PMC["BIOC"]}/BioC_json/{article_id}/unicode")
fail_check((response.status_code != 200), f"! Failed to GET {response.url} with code {response.status_code}")
try:
    response_data = response.json()
    print(f"DoiC JSON of {article_id}:\n {json.dumps(response_data, indent=4)}")
    print(response.url)
except:
    print(f"! Response from {response.url} is not in JSON format. Probably not found.")
    #print(response.content)
# Keep getting not found errors with the DoiC database. 
# Probably, not all papers are indexed in that format. I can't find a way to restrict the search to those that are.
# PMID vs PMCID? Sometimes articles are in DoiC, but only under one of the two IDs. Could use PMC ID API to translate.

# Get info from standard OA API
print("\n Requesting standard PMC info")
payload = {"id":article_id} # Does not support json :(
response = requests.get(PMC["OA"], params=payload)
fail_check((response.status_code != 200), f"! Failed to GET {response.url} with code {response.status_code}")
print(response.text)

if (pdf_url := parse_oa_file_url("pdf", response.text)) != None:
    print(f"\nPDF: {pdf_url}")
    if input("Download? (y/n): ").strip().lower() == "y":
        print("...")
        download_pmc_ftp(pdf_url, article_id+".pdf")
        print("Done!")
if (tar_url := parse_oa_file_url("tgz", response.text)) != None:
    print(f"\nTGZ: {tar_url}")
    if input("Download? (y/n): ").strip().lower() == "y":
        print("...")
        download_pmc_ftp(tar_url, article_id+".tar.gz")
        print("Done!")

