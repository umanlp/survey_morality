import sys, os
import configparser

import json
import bibtexparser

"""
This script converts a given .bib file to a corresponding .jsonl file.
For larger files (such as anthology+abstracts.bib), this takes several minutes.
"""

config_parser = configparser.ConfigParser()
config_parser.read(sys.argv[1])

infile_relpath = config_parser["I/O"]["infile_relpath"]

with open(infile_relpath) as bibtex_file:
   bibtex_database = bibtexparser.load(bibtex_file)

bibitems = bibtex_database.entries_dict

# if search_results/ does not already exist, create it:
if not os.path.exists(config_parser["I/O"]["output_dir"]):
    os.makedirs(config_parser["I/O"]["output_dir"])

outpath = config_parser["I/O"]["output_dir"] + config_parser["I/O"]["outfilename"]

with open(outpath, 'w', encoding='utf-8') as jsonf:
    json.dump(bibitems, jsonf, ensure_ascii=False, indent=3)


