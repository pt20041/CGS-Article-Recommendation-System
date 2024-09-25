import requests
import os

def search_openalex_works(query, cursor="*", count=10):
    url = "https://api.openalex.org/works"
    headers = {
        "User-Agent": "MyResearchApp/1.0 (mailto:ptakkar@terpmail.umd.edu)"
    }
    params = {
        "filter": f"display_name.search:{query}",
        "cursor": cursor,
        "per-page": count
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data from OpenAlex API: {response.status_code}")
        return None

def convert_abstract_inverted_index(abstract_inverted_index):
    if not abstract_inverted_index:
        return ""
    
    abstract_words = sorted(abstract_inverted_index.items(), key=lambda x: int(x[1][0]))
    abstract = ' '.join(word for word, positions in abstract_words)
    return abstract

def create_ris_entry(entry):
    ris_entry = []
    ris_entry.append("TY  - JOUR")
    
   
    ris_entry.append(f"TI  - {entry.get('title', '')}")
    
  
    for author in entry.get('authorships', []):
        ris_entry.append(f"AU  - {author.get('author', {}).get('display_name', '')}")
    
   
    ris_entry.append(f"JO  - {entry.get('host_venue', {}).get('display_name', '')}")
    ris_entry.append(f"PY  - {entry.get('publication_year', '')}")
    ris_entry.append(f"VL  - {entry.get('biblio', {}).get('volume', '')}")
    ris_entry.append(f"IS  - {entry.get('biblio', {}).get('issue', '')}")
    
   
    page_range = entry.get('biblio', {}).get('first_page', None)
    if page_range:
        ris_entry.append(f"SP  - {page_range}")
        ris_entry.append(f"EP  - {entry.get('biblio', {}).get('last_page', '')}")
    
    ris_entry.append(f"DO  - {entry.get('doi', '')}")
    ris_entry.append(f"UR  - {entry.get('id', '')}")
    
    
    concepts = entry.get('concepts', [])
    if concepts:
        for concept in concepts:
            ris_entry.append(f"KW  - {concept.get('display_name', '')}")
    
    abstract_inverted_index = entry.get('abstract_inverted_index', None)
    abstract = convert_abstract_inverted_index(abstract_inverted_index)
    if abstract:
        ris_entry.append(f"AB  - {abstract}")

    ris_entry.append("ER  - ")
    
    return "\n".join(ris_entry)

def generate_ris_file(json_data, filename="results_openalex.ris"):
    ris_content = ""
    if "results" in json_data:
        for entry in json_data["results"]:
            ris_content += create_ris_entry(entry) + "\n\n"
    
        with open(filename, "w", encoding="utf-8") as file:
            file.write(ris_content)
            print(f"RIS file saved as '{filename}'")
            
        os.startfile(filename)
    else:
        print("No entries found in JSON data.")

if __name__ == "__main__":
    query = "methane mitigation"
    
    all_results = []
    cursor = "*"
    for _ in range(10):
        # get next cursor
        json_results = search_openalex_works(query, cursor=cursor, count=10) 
        if json_results:
            all_results.extend(json_results.get('results', []))
            cursor = json_results.get('meta', {}).get('next_cursor')
            if not cursor:
                break
        else:
            break
    
    if all_results:
        json_data = {"results": all_results}
        generate_ris_file(json_data, filename=f"results_{query.replace(' ', '_')}.ris")

    print("\n" + "="*50 + "\n")