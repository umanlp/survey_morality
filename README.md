# A Survey on Modelling Morality for Text Analysis

## Requirements

The scripts were written in python3.10. The packages required to run the scripts are listed in `requirements.txt`.

## Survey methodology

### Paper sampling

Steps:

0. Manually downloaded search results from different sources are located here: `search_results/`
1. Search ACL for "moral":
	- unzip: `unzip acl_anthology_31_12_2023.zip`
	- run `python bib2json.py conf/bibjson.conf` to convert the downloaded anthology+abstracts.bib to a corresponding jsonl format
	- run `python acl_json_search.py conf/acl_json_search.conf` to collect ACL papers containing the keyword "moral"
2. Deduplicate and merge search results to a single file:
	- run `python merge_search_results.py conf/merge_search_results.conf`

The file resulting from step 2 is `unique_search_results_31_12_2023.jsonl` and contains all the files that went through the manual screening process explained below.

### Screening process

Screening was performed using `screening.ods`. The columns are defined as follows:
- Column A ("ID"): These bibkeys correspond to those in `unique_search_results_31_12_2023.jsonl`
- Column B ("Title"): Title of the paper
- Column C ("English"): Whether the paper is written in English
- Column D ("Accessible"): Whether the paper is accessible
- Column E ("Text/speech data"): Whether the methodology relies on text or speech data
- Column F ("Checked full-text"): Whether it was necessary to check more than just the title, abstract and keywords in order to decide whether to keep this paper
- Column G ("Passes screening"): Final decision for the paper in the screening process
- Column H ("Reasons to reject"): Why the paper was rejected in the screening process
- Column I ("Comments or contents of the paper"): Contribution(s) of the paper or a comment/note on the paper


### Snowballing

The spreadsheet `snowballing_candidates.ods` was used to collect papers found via backward snowballing. 
The columns are defined as follows:
- Column A ("ID"): Theses bibkeys correspond to those in `snowballing_candidates.bib`.
- Column B ("Title"): Title of the paper 
- Column C ("Passes screening"): Final decision for the paper in the screening process
- Column D ("Reasons to reject"): Why the paper was rejected in the screening process
- Column E ("Comments or contents of the paper"): Contribution(s) of the paper or a comment/note on the paper
- Column F ("Found where/how?"): How this paper was found in the backward snowballing process.

### Review process

Reviews for each paper were collected using the survey form in `survey_form/`. The survey form is accompanied by a codebook (`codebook.pdf`) that defines all the variables in the survey form and ensure consistent reviews.

For a given paper, the survey form saves the review to a file in json-format. The json-reviews for all 135 papers can be found in the following folder: `all_reviews/`.

### Consistency checks

Automated consistency checks were performed using `consistency_checks.py`. 
Results are written to `consistency_checks/`.


## Analyses

The following script was used to extract information from the collection of reviews: `analyze_reviews.py`. Results are written to `analysis_results/`.

## Checklist

The file `checklist.pdf` corresponds to the checklist we released along with our paper.