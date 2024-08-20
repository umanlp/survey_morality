import os
import json
import pandas as pd

def read_reviews(review_folder_relpath):
    bibkeys = []
    frames = []
    for filename in os.listdir(review_folder_relpath):
        if filename.endswith('.json'):
            with open(os.path.join(review_folder_relpath, filename)) as f:
                json_content = json.loads(f.read())
                for bibkey, content in json_content.items():
                    bibkeys.append(bibkey)
                    df = pd.DataFrame.from_dict(content, orient='index').T
                    frames.append(df)
    reviews = pd.concat(frames, keys=bibkeys).droplevel(level=1)
    return reviews

def keep_only_relevant(reviews):

    paper_type_var = ["typeResource", "typeApplicationAI", "typeNotRelevant", "typeExperiment", "typeAnalysis", "typeDemo"]
    non_radio_replace(reviews, paper_type_var)
    print("{} reviewed papers in total".format(len(reviews)))
    print("{} demo papers".format(len(reviews[(reviews["typeDemo"])])))
    print("{} not relevant papers".format(len(reviews[(reviews["typeNotRelevant"])])))
    only_relevant = reviews[(~reviews["typeNotRelevant"]) & (~reviews["typeDemo"])]
    
    #exclude Paulissen-Wendt (ValueEval submission) from stats
    only_relevant.drop(index="paulissen-wendt-2023-lauri", inplace=True)

    print("{} papers after dropping irrelevant, demo and 1 ValueEval paper".format(len(only_relevant)))

    return only_relevant

def non_radio_replace(df, var_list):
    for v in var_list:
        #print("{} papers of type {}".format(len(df[~df[v].isna()]), v))
        di = {v: True, None: False}
        df[v].replace(di, inplace=True)

def process_data_info(reviews):
    # data:
    languages_var = ["langEn", "langOther", "langNotSpecified"]
    non_radio_replace(reviews, languages_var)
    data_type_var = ["dataSM", "dataNews", "dataOther"]
    non_radio_replace(reviews, data_type_var)
    data_SM_type_var = ["dataSMTwitter", "dataSMReddit", "dataSMFacebook", "dataSMOther"] # only if data_type_var has dataSM True
    non_radio_replace(reviews, data_SM_type_var)
    domain_var = ["dataDomainPolitics", "dataDomainScience", "dataDomainLaw", "dataDomainReligion", "dataDomainFiction", "dataDomainOther"] # radio
    resources_used_var = ["resourcesDict", "resourcesDictValues", "resourcesMFTC", "resourcesMFRC", "resourcesMFQuestionnaire", "resourcesSocialChemistry", "resourcesScruples", "resourcesMoralStories", "resourcesEthics", "resourcesMoralStrength", "resourcesSemAxis", "resourcesHHH", "resourcesTrustfulQA", "resourcesOther"] # no one annotated "resourcesNorms", "resourcesMCM"
    non_radio_replace(reviews, resources_used_var)    
    #moral_theory_var = ["theoryMFT", "theoryHumanval", "theoryOther", "theoryOwn", "theoryNone"]
    moral_theory_var = ["theoryMFT", "theoryHumanval", "theoryOther", "theoryNone"]
    non_radio_replace(reviews, moral_theory_var)