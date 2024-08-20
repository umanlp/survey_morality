import sys, os
import configparser

import pandas as pd
#import matplotlib.pyplot as plt
import warnings

import survey_utils

"""
This script takes a folder containing reviews as input and writes some statistics about them
in a folder analysis_results/.

Usage:
python analyze_reviews.py conf/analyze_reviews.conf
"""

def goalCondition(s):
    if (s['goalFraming']) or (s['goalPerson']) or (s['goalSentiment']):
        return True
    else:
        return False
    
def clean_up_years(s):
    return int(s["year"].strip("a").strip("b"))

def resource_papers_infos(reviews):
    # papers proposing a resource
    resource_subfolder = analysis_outfolder + "resourceYes/"
    if not os.path.exists(resource_subfolder):
        os.makedirs(resource_subfolder)
    print("\n------------------------------\nResource papers:")
    resource_papers = reviews[reviews["resource"] == "resourceYes"]
    print("{} papers in total provide a resource.".format(len(resource_papers)))

    # contributions of res papers
    typeResource_includes = ["includesAnnotation", "includesOntology", "includesDictionary"]
    type_res_dict = {}
    for v in typeResource_includes:
        v_df = resource_papers[resource_papers[v] == True]
        count = len(v_df)
        type_res_dict[v] = count
        outfilename = v + ".tsv"
        with open(resource_subfolder + outfilename, "w") as outf:
            v_df[["title", "year", "bibKey", v, "langEn", "langOther", "langNotSpecified", "annotSizeText", "annotSetup", "annotViews", "AnnotSchema", "AnnotSchemaLen", "IAA", "annotIAATypeText", "annotIAAScoreText", "annotIAAMetricText", "AnnotErrAnalysis", "AnnotResourceAvailable"]].to_csv(outf, sep="\t", index=False)
    exp_df = pd.DataFrame(list(type_res_dict.items()), columns=['contribution','count'])
    exp_df.sort_values(by="count", inplace=True, ascending=False)
    with open(resource_subfolder + "resContribution.tsv", "w") as outf:
        exp_df.to_csv(outf, sep="\t", index=False)


    #print("Are annotators trained?")
    #print(resource_papers["annotSetup"].value_counts())
    #labels = []
    #resource_papers["annotSetup"].value_counts().plot(kind="pie", title="Annotation setup", labels=labels)
    #plt.savefig(resource_subfolder + 'annotSetup.png')
    with open(resource_subfolder + "annotSetup.tsv", "w") as outf:
        resource_papers["annotSetup"].value_counts().to_csv(outf, sep="\t")

    #print("\nIs there information about annotators' demographics/political views?")
    #print(resource_papers["annotViews"].value_counts())
    with open(resource_subfolder + "annotViews.tsv", "w") as outf:
        resource_papers["annotViews"].value_counts().to_csv(outf, sep="\t")

    #print("\nAre annotation guidelines available?")
    #print(resource_papers["AnnotSchema"].value_counts())
    with open(resource_subfolder + "AnnotSchema.tsv", "w") as outf:
        resource_papers["AnnotSchema"].value_counts().to_csv(outf, sep="\t")

    guidelines_available = resource_papers[resource_papers["AnnotSchema"] == "AnnotSchemaYes"]
    #print("When guidelines are available, these are the value counts for guidelines lengths:")
    #print(guidelines_available["AnnotSchemaLen"].value_counts())
    with open(resource_subfolder + "AnnotSchemaLen.tsv", "w") as outf:
        guidelines_available["AnnotSchemaLen"].value_counts().to_csv(outf, sep="\t")

    #print("\nDoes the paper report IAA?")
    #print(resource_papers["IAA"].value_counts())
    with open(resource_subfolder + "IAA.tsv", "w") as outf:
        resource_papers["IAA"].value_counts().to_csv(outf, sep="\t")

    #print("\nDoes the paper report an error analysis for the annotations?")
    #print(resource_papers["AnnotErrAnalysis"].value_counts())
    with open(resource_subfolder + "AnnotErrAnalysis.tsv", "w") as outf:
        resource_papers["AnnotErrAnalysis"].value_counts().to_csv(outf, sep="\t")

    #print("\nIs the resource presented in the paper available?")
    #print(resource_papers["AnnotResourceAvailable"].value_counts())
    with open(resource_subfolder + "AnnotResourceAvailable.tsv", "w") as outf:
        resource_papers["AnnotResourceAvailable"].value_counts().to_csv(outf, sep="\t")

    print("{} out of {} crowdsourcing papers collect information about coders' demographics or their political or moral views.".format(len(resource_papers[(resource_papers["annotSetup"] == "annotCrowd") & (resource_papers["annotViews"] == "annotViewsYes")]), len(resource_papers[resource_papers["annotSetup"] == "annotCrowd"])))

def experimental_papers_infos(reviews):
    # papers containing experiments
    experiment_subfolder = analysis_outfolder + "experimentYes/"
    if not os.path.exists(experiment_subfolder):
        os.makedirs(experiment_subfolder)
    print("\n------------------------------\nExperimental papers:")
    experimental_papers = reviews[reviews["experiment"] == "experimentYes"]
    print("{} papers in total provide experiments.".format(len(experimental_papers)))

    exp_var = ["ruleML", "featML", "logicML", "expTransformers", "expReinforcement", "expLlm", "semiML", "unsuperML", "expOther"]
    exp_dict = {}
    survey_utils.non_radio_replace(experimental_papers, exp_var)
    for v in exp_var:
        count = len(experimental_papers[experimental_papers[v]])
        #print("{} experimental papers provide experiments with {}".format(count, v))
        exp_dict[v] = count
    exp_df = pd.DataFrame(list(exp_dict.items()), columns=['method','count'])
    exp_df.sort_values(by="count", inplace=True, ascending=False)
    with open(experiment_subfolder + "expMethod.tsv", "w") as outf:
        exp_df.to_csv(outf, sep="\t", index=False)

    #print("\nDoes the paper include some kind of error analysis for the experiments?")
    #print(experimental_papers["ExpErrAnalysis"].value_counts())
    with open(experiment_subfolder + "ExpErrAnalysis.tsv", "w") as outf:
        experimental_papers["ExpErrAnalysis"].value_counts().to_csv(outf, sep="\t")

    #print("\nAre the gold labels clearly defined or do they have to be infered? (only relevant for supervised ML)")
    #print(experimental_papers["replicGold"].value_counts())
    with open(experiment_subfolder + "replicGold.tsv", "w") as outf:
        experimental_papers["replicGold"].value_counts().to_csv(outf, sep="\t")

def analysis_papers_infos(reviews):
    # papers including an analysis
    analysis_subfolder = analysis_outfolder + "analysisYes/"
    if not os.path.exists(analysis_subfolder):
        os.makedirs(analysis_subfolder)
    print("\n------------------------------\nAnalysis papers:")
    analysis_papers = reviews[reviews["analysis"] == "analysisYes"]
    print("{} papers in total provide analyses.".format(len(analysis_papers)))

    analysis_methods = ["resourcesDict", "resourcesOtherText", "includesRuleBased", "includesLogicBased", "includesUnsupervised", "includesSupervised", "expTransformers", "includesLLMPrompt", "expLlm"]
    methods_report = analysis_papers[["title", "typeAnalysis", "experiment"] + analysis_methods]
    methods_report.fillna(False, inplace=True)
    with open(analysis_subfolder + "analysisMethodsReport.tsv", "w") as outf:
        methods_report.to_csv(outf, sep="\t")

    print("{} analysisYes papers also have typeAnalysis".format(len(methods_report[methods_report["typeAnalysis"] == True])))
    print("{} analysisYes papers use the MFD or a variant thereof".format(len(methods_report[methods_report["resourcesDict"] == True])))
    print("{} analysisYes papers use the MFD or a variant thereof, in combination with either a rule-based or unsupervised method to detect/classify moral foundations.".format(len(methods_report[(methods_report["resourcesDict"] == True) & ((methods_report["includesUnsupervised"] == True)|(methods_report["includesRuleBased"] == True))])))
    print("{} analysisYes papers use either fine-tuned Transformers or zero- or few-shot LLMs without fine-tuning for the detection/classification of moral values.".format(len(methods_report[methods_report[["expTransformers", "includesLLMPrompt", "expLlm"]].any(axis=1)])))

    #print("\nResearch field / background of the paper")
    #print(analysis_papers["analysisField"].value_counts())
    with open(analysis_subfolder + "analysisField.tsv", "w") as outf:
        analysis_papers["analysisField"].value_counts().to_csv(outf, sep="\t")

    #print("\nThe analysis includes:")
    #print(analysis_papers["analysisType"].value_counts())
    with open(analysis_subfolder + "analysisType.tsv", "w") as outf:
        analysis_papers["analysisType"].value_counts().to_csv(outf, sep="\t")


def replicability_info(reviews):
    # replicability and validation
    data_avail_var = ["dataAvailYes", "dataAvailPartly", "dataAvailNo", "dataAvailNoInfo", "dataAvailNotRelevant"] # radio
    preproc_var = ["replicPreprocClear", "replicPreprocAmbig", "replicPreprocUnclear", "replicPreprocNotRelevant"] # radio
    code_avail_var = ["replicCodeYes", "replicCodeNo", "replicCodeNotRelevant"] # radio
    validation_var = ["validationHypothesis", "validationAnnotation", "validationCorrelation", "validationTriangulation", "validationOther", "validationNone"]
    survey_utils.non_radio_replace(reviews, validation_var)
    validation_dict = {}
    for v in validation_var:
        count = len(reviews[reviews[v]])
        #print("{} papers include validation through {}".format(count, v))
        validation_dict[v] = count  
    validation_df = pd.DataFrame(list(validation_dict.items()), columns=['validationMethod','count'])
    validation_df.sort_values(by="count", inplace=True, ascending=False)
    with open(analysis_outfolder + "validationMethod.tsv", "w") as outf:
        validation_df.to_csv(outf, sep="\t", index=False)
              

def modelling_morality_info(reviews):
    moral_theory_dict = {}
    #moral_theory_var = ["theoryMFT", "theoryHumanval", "theoryOther", "theoryOwn", "theoryNone"]
    moral_theory_var = ["theoryMFT", "theoryHumanval", "theoryOther", "theoryNone"]
    survey_utils.non_radio_replace(reviews, moral_theory_var)
    for v in moral_theory_var:
        count = len(reviews[reviews[v]])
        #print("{} papers model morality through {}".format(count, v))
        moral_theory_dict[v] = count
    moral_theory_df = pd.DataFrame(list(moral_theory_dict.items()), columns=['theory','count'])
    moral_theory_df.sort_values(by="count", inplace=True, ascending=False)
    theory_names = {"theoryMFT": "MFT", "theoryNone": "No theory", "theoryHumanval": "Schwartz' Human Values", "theoryOther": "Other"}
    moral_theory_df["theory"] = moral_theory_df["theory"].apply(lambda row: theory_names[row])
    with open(analysis_outfolder + "moralTheory.tsv", "w") as outf:
        moral_theory_df.to_csv(outf, sep="\t", index=False)

    mft_papers = reviews[reviews["theoryMFT"]]
    mft_number_var = ["numMF5", "numMF10", "numMF6Liberty", "numMF12Liberty", "numMF6", "numMF12", "numMF7", "numMF14", "numMFOwn", "numMFNotSpecified"] # radio
    assert len(mft_papers) == sum(mft_papers["numMF"].value_counts())
    #print("Value counts for the number of MF categories used:")
    #print(mft_papers["numMF"].value_counts())
    with open(analysis_outfolder + "numMFValueCounts.tsv", "w") as outf:
        mft_papers["numMF"].value_counts().to_csv(outf, sep="\t")
    #definition_var = ["definitionYes", "definitionVague", "definitionNo"] # radio
    #print("\nHow extensively papers define morality:")
    #print(reviews["definition"].value_counts())
    with open(analysis_outfolder + "moralityDefinition.tsv", "w") as outf:
        reviews["definition"].value_counts().to_csv(outf, sep="\t")

    level_dict = {}
    level_var = ["unitDocument", "unitSegment", "unitSentence", "unitToken", "unitFrame"]
    survey_utils.non_radio_replace(reviews, level_var)
    for v in level_var:
        count = len(reviews[reviews[v]])
        #print("{} papers model on the level of {}".format(count, v))
        level_dict[v] = count
    level_df = pd.DataFrame(list(level_dict.items()), columns=['level','count'])
    level_df.sort_values(by="count", inplace=True, ascending=False)
    level_df["level"] = level_df["level"].apply(lambda row: row.replace("unit", ""))
    with open(analysis_outfolder + "modellingMoralityLevel.tsv", "w") as outf:
        level_df.to_csv(outf, sep="\t", index=False)

    purpose_var = ["goalFraming", "goalPerson", "goalSentiment", "goalComparison", "goalTheoryMoral", "goalTheoryOther", "goalAI"]
    for v in purpose_var:
        di = {v: True, None: False}
        reviews[v].replace(di, inplace=True)
    reviews['goalFramingPersonSentiment'] = reviews.apply(goalCondition, axis=1)
    reviews.drop(columns=["goalFraming", "goalPerson", "goalSentiment"], inplace=True)
    purpose_dict = {}
    for v in ["goalFramingPersonSentiment", "goalComparison", "goalTheoryMoral", "goalTheoryOther", "goalAI"]:
        count = len(reviews[reviews[v]])
        purpose_dict[v] = count
        #print("{} papers model morality with the following goal: {}".format(count, v))
    purpose_df = pd.DataFrame(list(purpose_dict.items()), columns=['purpose','count'])
    purpose_df.sort_values(by="count", inplace=True, ascending=False)
    goal_names = {"goalFramingPersonSentiment": "Value/Stance/Framing", "goalAI": "Morality in AI", "goalComparison": "Comparison", "goalTheoryMoral": "Moral Theories", "goalTheoryOther": "Other Theories"}
    purpose_df["purpose"] = purpose_df["purpose"].apply(lambda row: goal_names[row])
    purpose_df.rename(columns={"purpose": "Objective", "count": "Count"}, inplace=True)
    with open(analysis_outfolder + "modellingMoralityPurpose.tsv", "w") as outf:
        purpose_df.to_csv(outf, sep="\t", index=False)

    return moral_theory_dict, level_dict, purpose_dict

def basic_stats(reviews):

    metadata_var = ["bibkey", "year", "authors", "title", "paperType", "contentLength"]
    includes_var = ["includesDictionary", "includesOntology", "includesAnnotation", "includesRuleBased", "includesLogicBased", "includesUnsupervised", "includesSupervised", "includesLLMPrompt", "includesProbing", "includesAsFeat", "includesApplication"]
    paper_type_var = ["typeResource", "typeApplicationAI", "typeNotRelevant", "typeExperiment", "typeAnalysis", "typeDemo"]
    survey_utils.non_radio_replace(reviews, paper_type_var)
    
    survey_utils.non_radio_replace(reviews, includes_var)
    #print("\nContent length value counts:\n{}".format(reviews["paperContentLength"].value_counts()))
    with open(analysis_outfolder + "paperContentLength.tsv", "w") as outf:
        reviews["paperContentLength"].value_counts().to_csv(outf, sep="\t")

    reviews['year'] = reviews.apply(clean_up_years, axis=1)
    #print("\nPublication year value counts:\n{}".format(only_relevant["year"].value_counts()))
    with open(analysis_outfolder + "year_value_counts.tsv", "w") as outf:
        reviews["year"].value_counts().to_csv(outf, sep="\t")

    print("------------------------------")
    # Papers that work with languages other than English
    non_eng = reviews[reviews["langOther"] != "--"]
    print("{} papers work with languages other than English.".format(len(non_eng)))
    print("{} non-English release an annotated dataset.".format(len(non_eng[non_eng["includesAnnotation"]])))
    non_eng_dict_based = non_eng[((~non_eng["resourcesDict"].isna()) | (~non_eng["resourcesMoralStrength"].isna())) & ((non_eng["includesRuleBased"]) | (non_eng["includesUnsupervised"]))]
    print("{} non-English papers use a dictionary in combination with rule-based or unsupervised classification".format(len(non_eng_dict_based)))

    return reviews

if __name__ == '__main__':
    pd.options.mode.chained_assignment = None  # default='warn'
    warnings.simplefilter(action='ignore', category=FutureWarning)

    config_parser = configparser.ConfigParser()
    config_parser.read(sys.argv[1])

    review_folder_relpath = config_parser["I/O"]["review_folder_relpath"]
    reviews = survey_utils.read_reviews(review_folder_relpath)

    analysis_outfolder = "analysis_results/"
    if not os.path.exists(analysis_outfolder):
        os.makedirs(analysis_outfolder)

    only_relevant = survey_utils.keep_only_relevant(reviews)
    basic_stats(only_relevant)

    # modelling morality:
    moral_theory_dict, level_dict, purpose_dict = modelling_morality_info(only_relevant)

    survey_utils.process_data_info(only_relevant)

    replicability_info(only_relevant)

    #####################################
    ## paper type specific annotations ##
    #####################################
    resource_papers_infos(only_relevant)

    experimental_papers_infos(only_relevant)

    analysis_papers_infos(only_relevant)

    print("")