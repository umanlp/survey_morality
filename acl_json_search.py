import sys, os
import configparser

import json

"""
Search a given ACL anthology file (in jsonl format) for the keyword "moral" in abstract or title.

Save search results to json file provided in outfilename.
"""



with open(acl_relpath, "r") as infile:
    acl = json.loads(infile.read())

moral_papers = dict()

# replace } and {, lowercase and search for "moral" in abstract or title:
for bibitem, fields in acl.items():
    raw_title = fields["title"].lower().replace("{", "").replace("}", "")
    if "abstract" in fields:
        raw_abstract = fields["abstract"].lower().replace("{", "").replace("}", "")
    else:
        raw_abstract = ""

    if "moral" in raw_title or "moral" in raw_abstract:
        moral_papers[bibitem] = fields
        #print(fields["title"])

# if search_results/ does not already exist, create it:
if not os.path.exists(config_parser["I/O"]["output_dir"]):
    os.makedirs(config_parser["I/O"]["output_dir"])

# save results in json format:
outfilename = config_parser["I/O"]["output_dir"] + "acl.jsonl"
with open(outfilename, 'w', encoding='utf-8') as jsonf:
    json.dump(moral_papers, jsonf, ensure_ascii=False, indent=3)

print("")
