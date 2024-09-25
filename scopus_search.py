import requests
import os

def search_scopus_json(api_key, query, start, count=10):
    url = "https://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }
    params = {
        "query": query,
        "start": start,
        "count": count
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data from Scopus API: {response.status_code}")
        return None

def create_ris_entry(entry):
    ris_entry = []
    ris_entry.append("TY  - JOUR")
    ris_entry.append(f"TI  - {entry.get('dc:title', '')}")
    ris_entry.append(f"AU  - {entry.get('dc:creator', '')}")
    ris_entry.append(f"JO  - {entry.get('prism:publicationName', '')}")
    ris_entry.append(f"PY  - {entry.get('prism:coverDate', '').split('-')[0]}")
    ris_entry.append(f"VL  - {entry.get('prism:volume', '')}")
    ris_entry.append(f"IS  - {entry.get('prism:issueIdentifier', '')}")
    
    page_range = entry.get('prism:pageRange', None)
    if page_range:
        pages = page_range.split('-')
        if len(pages) == 2:
            ris_entry.append(f"SP  - {pages[0]}")
            ris_entry.append(f"EP  - {pages[1]}")
    
    ris_entry.append(f"DO  - {entry.get('prism:doi', '')}")

    scopus_link = ""
    for link in entry.get('link', []):
        if link.get('@ref') == 'scopus':
            scopus_link = link.get('@href', '')
            break
    if scopus_link:
        ris_entry.append(f"UR  - {scopus_link}")

    ris_entry.append("ER  - ")
    
    return "\n".join(ris_entry)

def generate_ris_file(json_data, filename="results.ris"):
    ris_content = ""
    if "entry" in json_data["search-results"]:
        for entry in json_data["search-results"]["entry"]:
            ris_content += create_ris_entry(entry) + "\n\n"
    
        with open(filename, "w", encoding="utf-8") as file:
            file.write(ris_content)
            print(f"RIS file saved as '{filename}'")
            
        os.startfile(filename)
    else:
        print("No entries found in JSON data.")

if __name__ == "__main__":
    api_key = "7a67f5af0f1f6829f4c4eb0091532f3b"
    
    queries = [
        "TITLE-ABS-KEY(\"Leak Detection and Repair\" OR LDAR OR \"Methane Mitigation\" OR \"Fugitive Emissions Detection\")"
    ]
    
    for query in queries:
        print(f"Searching for query: {query}")
        all_results = []
        
        # method to get more than 20 results
        for start in range(0, 100, 10):
            json_results = search_scopus_json(api_key, query, start=start, count=10)
            if json_results:
                all_results.extend(json_results['search-results'].get('entry', []))
        
        if all_results:
            json_data = {"search-results": {"entry": all_results}}
            generate_ris_file(json_data, filename=f"results_{query[:10]}.ris")
        
        print("\n" + "="*50 + "\n")