import sys, os
import configparser

import json
import bibtexparser

"""
Takes a folder containing .bib or .jsonl files as input.
Counts papers, de-duplicates them based on bibkey and title.
Saves the resulting unique papers to a jsonl file.
"""

jsonl_papers_list = []
jsonl_papers_dict = {}
bibtex_papers_list = []
bibtex_papers_dict = {}

config_parser = configparser.ConfigParser()
config_parser.read(sys.argv[1])

search_results_path = config_parser["I/O"]["search_results_relpath"]

for filename in os.listdir(search_results_path):
    if filename.endswith('.jsonl'):
        with open(os.path.join(search_results_path, filename)) as f:
            jsonl_papers_content = json.loads(f.read())
            print(filename, ":", len(jsonl_papers_content))
        jsonl_papers_list.append((filename, jsonl_papers_content))
    elif filename.endswith('.bib'):
        with open(os.path.join(search_results_path, filename)) as f:
            bibtex_papers_content = bibtexparser.load(f)
            print(filename, ":", len(bibtex_papers_content.entries))
        bibtex_papers_list.append((filename, bibtex_papers_content))

# collect and count all papers from both source types (jsonl and bibtex)
papers = {}
bibkey_sources = {}
count = 0
for tup in jsonl_papers_list:
    source, data = tup
    count += len(data)
    papers.update(data) # this already checks for duplicate bibkeys
    for d in data:
        bibkey_sources[d] = source

for tup in bibtex_papers_list:
    source, data = tup
    count += len(data.entries_dict)
    bibitems = data.entries_dict
    papers.update(bibitems)
    for b in bibitems:
        bibkey_sources[b] = source

print(count, "papers BEFORE dropping duplicates")

# collect unique papers:
titles = []
unique_papers = {}
for bibkey, fields in papers.items():
    title = fields["title"].replace("{", "").replace("}", "").replace("\n", " ").replace("&nbsp;", " ").replace("&amp;", " ").replace("  ", " ")
    title = title.replace("  ", " ")
    fields["source"] = bibkey_sources[bibkey]
    fields["title"] = title
    title = title.lower()
    if title not in titles: # now we additionally check for duplicate titles
        unique_papers[bibkey] = fields
    titles.append(title)

print(len(unique_papers), "papers AFTER dropping duplicates")

with open(config_parser["I/O"]["outfilename"], 'w', encoding='utf-8') as jsonf:
    json.dump(unique_papers, jsonf, ensure_ascii=False, indent=3)