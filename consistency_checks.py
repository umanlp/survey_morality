import sys, os
import configparser

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import survey_utils

"""
This script takes a folder containing reviews as input and runs consistency checks on the reviews.
If potential inconsistencies are found, they are written to a folder consistency_checks/.
These checks should help identify *potential* inconsistencies in paper reviews.

Usage:
python consistency_checks.py conf/consistency_checks.conf
"""


def check_type_radio(reviews):

    checked_dict = {}

    exp_papers = reviews[reviews["typeExperiment"]]
    not_matching_exp = exp_papers[exp_papers["experiment"] == "experimentNo"][["title", "typeExperiment", "experiment"]]
    if len(not_matching_exp) > 0:
        checked_dict["not_matching_exp.tsv"] = not_matching_exp

    res_papers = reviews[reviews["typeResource"]]
    not_matching_res = res_papers[res_papers["resource"] == "resourceNo"][["title", "typeResource", "resource"]]
    if len(not_matching_res) > 0:
        checked_dict["not_matching_res.tsv"] = not_matching_res

    an_papers = reviews[reviews["typeAnalysis"]]
    not_matching_an = an_papers[an_papers["analysis"] == "analysisNo"][["title", "typeAnalysis", "analysis"]]
    if len(not_matching_an) > 0:
        checked_dict["not_matching_an.tsv"] = not_matching_an

    return checked_dict

def check_type_contributions(reviews):

    checked_dict = {}

    # experimentYes must have one of typeExperiment_includes
    typeExperiment_includes = ["includesRuleBased", "includesUnsupervised", "includesSupervised", "includesLogicBased", "includesLLMPrompt", "expReinforcement", "expLlm"]
    exp_papers = reviews[reviews["experiment"] == "experimentYes"]
    not_including_exp = exp_papers[~exp_papers[typeExperiment_includes].any(axis=1)][typeExperiment_includes + ["title", "experiment"]]
    if len(not_including_exp) > 0:
        checked_dict["not_including_exp.tsv"] = not_including_exp
    
    typeResource_includes = ["includesAnnotation", "includesOntology", "includesDictionary"]
    res_papers = reviews[reviews["resource"] == "resourceYes"]
    not_including_res = res_papers[~res_papers[typeResource_includes].any(axis=1)][typeResource_includes + ["title", "resource"]]
    if len(not_including_res) > 0:
        checked_dict["not_including_res.tsv"] = not_including_res

    anno_papers = reviews[~reviews["includesAnnotation"].isna()]
    onto_papers = reviews[~reviews["includesOntology"].isna()]
    dict_papers = reviews[~reviews["includesDictionary"].isna()]

    anno_no_res = anno_papers[anno_papers["resource"] != "resourceYes"][["title", "resource", "includesAnnotation"]]
    if len(anno_no_res) > 0:
        checked_dict["anno_no_res.tsv"] = anno_no_res

    onto_no_res = onto_papers[onto_papers["resource"] != "resourceYes"][["title", "resource", "includesOntology"]]
    if len(onto_no_res) > 0:
        checked_dict["onto_no_res.tsv"] = onto_no_res

    dict_no_res = dict_papers[dict_papers["resource"] != "resourceYes"][["title", "resource", "includesDictionary"]]
    if len(dict_no_res) > 0:
        checked_dict["dict_no_res.tsv"] = dict_no_res

    return checked_dict

def check_length(reviews):

    checked_dict = {}

    missing_lengths = reviews[(reviews["paperContentLength"] == "--") | (reviews["paperTotalLength"] == "--")][["title", "paperContentLength", "paperTotalLength"]]
    if len(missing_lengths) > 0:
        checked_dict["missing_lengths.tsv"] = missing_lengths

    remaining = reviews[~reviews.index.isin(missing_lengths.index)]
    wrong_lengths = remaining[remaining["paperContentLength"].apply(int) > remaining["paperTotalLength"].apply(int)][["title", "paperContentLength", "paperTotalLength"]]
    if len(wrong_lengths) > 0:
        checked_dict["wrong_lengths.tsv"] = wrong_lengths

    return checked_dict

def check_lang(reviews):

    checked_dict = {}

    lang_en_and_not_specified = reviews[reviews["langEn"] & reviews["langNotSpecified"]][["title", "langEn", "langOther", "langNotSpecified"]]
    if len(lang_en_and_not_specified) > 0:
        checked_dict["lang_en_and_not_specified.tsv"] = lang_en_and_not_specified

    lang_no_info = reviews[~reviews["langEn"] & ~reviews["langNotSpecified"] & (reviews["langOther"] == "--")][["title", "langEn", "langOther", "langNotSpecified"]]
    if len(lang_no_info) > 0:
        checked_dict["lang_no_info.tsv"] = lang_no_info

    return checked_dict

def check_dataSM(reviews):

    checked_dict = {} 

    sm_options = ["dataSMTwitter", "dataSMReddit", "dataSMFacebook", "dataSMOther"]

    sm_reviews = reviews[reviews["dataSM"]]

    missing_dataSM = sm_reviews[~sm_reviews[sm_options].any(axis=1)]
    if len(missing_dataSM) > 0:
        checked_dict["missing_dataSM.tsv"] = missing_dataSM

    return checked_dict

def check_text_fields(reviews):

    checked_dict = {}

    missing_otherTheory = reviews[reviews["theoryOther"] & reviews["theoryOtherText"] == "--"][["title", "theoryOther", "theoryOtherText"]]
    if len(missing_otherTheory) > 0:
        checked_dict["missing_otherTheory.tsv"] = missing_otherTheory

    missing_dataOther = reviews[reviews["dataOther"] & reviews["dataOtherText"] == "--"][["title", "dataOther", "dataOtherText"]]
    if len(missing_dataOther) > 0:
        checked_dict["missing_dataOther.tsv"] = missing_dataOther

    missing_domainOther = reviews[(reviews["dataDomain"] == "dataDomainOther") & (reviews["dataDomainOtherText"] == "--")][["title", "dataDomain", "dataDomainOtherText"]]
    if len(missing_domainOther) > 0:
        checked_dict["missing_domainOther.tsv"] = missing_domainOther

    missing_resOther = reviews[reviews["resourcesOther"] & reviews["resourcesOtherText"] == "--"][["title", "resourcesOther", "resourcesOtherText"]]
    if len(missing_resOther) > 0:
        checked_dict["missing_resOther.tsv"] = missing_resOther

    missing_annotsize = reviews[(reviews["resource"] == "resourceYes") & reviews["annotSizeText"] == "--"][["title", "resource", "annotSizeText"]]
    if len(missing_annotsize) > 0:
        checked_dict["missing_annotsize.tsv"] = missing_annotsize

    missing_iaafields = reviews[(reviews["IAA"] == "IAAYes") & ((reviews["annotIAATypeText"] == "--") | (reviews["annotIAAScoreText"] == "--") | (reviews["annotIAAMetricText"] == "--"))][["title", "IAA", "annotIAATypeText", "annotIAAScoreText", "annotIAAMetricText"]]
    if len(missing_iaafields) > 0:
        checked_dict["missing_iaafields.tsv"] = missing_iaafields

    missing_resurl = reviews[(reviews["AnnotResourceAvailable"] == "AnnotResourceAvailableYes") & reviews["AnnotResourceAvailableYesURL"] == "--"][["title", "AnnotResourceAvailable", "AnnotResourceAvailableYesURL"]]
    if len(missing_resurl) > 0:
        checked_dict["missing_resurl.tsv"] = missing_resurl

    missing_resurlpart = reviews[(reviews["AnnotResourceAvailable"] == "AnnotResourceAvailablePartly") & reviews["AnnotResourceAvailablePartlyURL"] == "--"][["title", "AnnotResourceAvailable", "AnnotResourceAvailablePartlyURL"]]
    if len(missing_resurlpart) > 0:
        checked_dict["missing_resurlpart.tsv"] = missing_resurlpart

    missing_transf = reviews[(reviews["expTransformers"] == "expTransformers") & (reviews["expTransformerText"] == "--")][["title", "expTransformers", "expTransformerText"]]
    if len(missing_transf) > 0:
        checked_dict["missing_transf.tsv"] = missing_transf

    missing_expllm = reviews[(reviews["expLlm"] == "expLlm") & (reviews["expLlmText"] == "--")][["title", "expLlm", "expLlmText"]]
    if len(missing_expllm) > 0:
        checked_dict["missing_expllm.tsv"] = missing_expllm

    missing_semiml = reviews[(reviews["semiML"] == "semiML") & (reviews["semiMLText"] == "--")][["title", "semiML", "semiMLText"]]
    if len(missing_semiml) > 0:
        checked_dict["missing_semiml.tsv"] = missing_semiml

    missing_unsuperml = reviews[(reviews["unsuperML"] == "unsuperML") & (reviews["unsuperMLText"] == "--")][["title", "unsuperML", "unsuperMLText"]]
    if len(missing_unsuperml) > 0:
        checked_dict["missing_unsuperml.tsv"] = missing_unsuperml

    missing_analysisOther = reviews[(reviews["analysisField"] == "analysisFieldOther") & (reviews["analysisFieldOtherText"] == "--")][["title", "analysisField", "analysisFieldOtherText"]]
    if len(missing_analysisOther) > 0:
        checked_dict["missing_analysisOther.tsv"] = missing_analysisOther

    missing_expOther = reviews[(reviews["expOther"] == "expOther") & (reviews["expOtherText"] == "--")][["title", "expOther", "expOtherText"]]
    if len(missing_expOther) > 0:
        checked_dict["missing_expOther.tsv"] = missing_expOther

    missing_dataURL = reviews[(reviews["dataAvail"] == "dataAvailYes") & (reviews["dataYesUrlText"] == "--")][["title", "dataAvail", "dataYesUrlText"]]
    if len(missing_dataURL) > 0:
        checked_dict["missing_dataURL.tsv"] = missing_dataURL

    missing_dataURLpart = reviews[(reviews["dataAvail"] == "dataAvailPartly") & (reviews["dataPartlyUrlText"] == "--")][["title", "dataAvail", "dataPartlyUrlText"]]
    if len(missing_dataURLpart) > 0:
        checked_dict["missing_dataURLpart.tsv"] = missing_dataURLpart

    missing_codeURL = reviews[(reviews["replicCode"] == "replicCodeYes") & (reviews["replicCodeText"] == "--")][["title", "replicCode", "replicCodeText"]]
    if len(missing_codeURL) > 0:
        checked_dict["missing_codeURL.tsv"] = missing_codeURL

    missing_valOther = reviews[(reviews["validationOther"] == "validationOther") & (reviews["validationOtherText"] == "--")][["title", "validationOther", "validationOtherText"]]
    if len(missing_valOther) > 0:
        checked_dict["missing_valOther.tsv"] = missing_valOther

    return checked_dict

def check_vars_have_values(reviews):

    checked_dict = {}
    includes_var = ["includesDictionary", "includesOntology", "includesAnnotation", "includesRuleBased", "includesLogicBased", "includesUnsupervised", "includesSupervised", "includesLLMPrompt", "includesProbing", "includesAsFeat", "includesApplication"]
    survey_utils.non_radio_replace(reviews, includes_var)
    # if experimentYes, then the conditional variables related to it must all have values
    exp_var = ["ruleML", "featML", "logicML", "expTransformers", "expReinforcement", "expLlm", "semiML", "unsuperML", "expOther"]
    exp_papers = reviews[reviews["experiment"] == "experimentYes"]
    missing_method_exp = exp_papers[~exp_papers[exp_var].any(axis=1)][exp_var + ["title", "experiment"]]
    if len(missing_method_exp) > 0:
        checked_dict["missing_method_exp.tsv"] = missing_method_exp

    exp_radio = ["ExpErrAnalysis", "replicTrainTest", "replicGold"]
    missing_radio_exp = exp_papers[~exp_papers[exp_radio].all(axis=1)][exp_radio + ["title", "experiment"]]
    if len(missing_radio_exp) > 0:
        checked_dict["missing_radio_exp.tsv"] = missing_radio_exp

    # if resourceYes, then the conditional variables related to it must all have values
    res_papers = reviews[reviews["resource"] == "resourceYes"]
    res_radio = ["annotSetup", "annotViews", "AnnotSchema", "IAA", "AnnotErrAnalysis", "AnnotResourceAvailable"]
    missing_radio_res = res_papers[~res_papers[res_radio].all(axis=1)][res_radio + ["title", "resource"]]
    if len(missing_radio_res) > 0:
        checked_dict["missing_radio_res.tsv"] = missing_radio_res

    # if analysisYes, then the conditional variables related to it must all have values
    an_papers = reviews[reviews["analysis"] == "analysisYes"]
    an_radio = ["analysisField", "analysisType"]
    missing_radio_an = an_papers[~an_papers[an_radio].all(axis=1)][an_radio + ["title", "analysis"]]
    if len(missing_radio_an) > 0:
        checked_dict["missing_radio_an.tsv"] = missing_radio_an

    # replicability and validation
    validation_var = ["validationHypothesis", "validationAnnotation", "validationCorrelation", "validationTriangulation", "validationOther", "validationNone"]
    missing_validation = reviews[~reviews[validation_var].any(axis=1)][validation_var + ["title"]]
    if len(missing_validation) > 0:
        checked_dict["missing_validation.tsv"] = missing_validation

    validation_radio = ["dataAvail", "replicPreproc", "replicCode"]
    missing_radio_val = reviews[~reviews[validation_radio].all(axis=1)][validation_radio + ["title"]]
    if len(missing_radio_val) > 0:
        checked_dict["missing_radio_val.tsv"] = missing_radio_val

    ####### mismatches between certain experiment variables #######

    # if includesSupervised, expLlm cannot be the only method used
    exp_var_except_expLlm = exp_var.copy()
    exp_var_except_expLlm.remove("expLlm")
    supervised_papers = exp_papers[exp_papers["includesSupervised"]]
    mismatch_supervised = supervised_papers[(~supervised_papers[exp_var_except_expLlm].any(axis=1)) & (~supervised_papers["expLlm"].isna())][exp_var + ["title", "experiment", "includesSupervised"]]
    if len(mismatch_supervised) > 0:
        checked_dict["mismatch_supervised.tsv"] = mismatch_supervised

    # if "expTransformers" is true, then "includesSupervised" must also be true
    transf_papers = reviews[~reviews["expTransformers"].isna()]
    mismatch_transf = transf_papers[~transf_papers["includesSupervised"]][["title", "expTransformers", "includesSupervised"]]
    if len(mismatch_transf) > 0:
        checked_dict["mismatch_transf.tsv"] = mismatch_transf

    # if "includesUnsupervised" is true and "experimentYes" then either "semiML", "unsuperML" or "expOther" must be true
    mismatch_semi_unsuper = exp_papers[(exp_papers["includesUnsupervised"]) & ((exp_papers["semiML"].isna()) & (exp_papers["unsuperML"].isna()) & (exp_papers["expOther"].isna()))][["title", "experiment", "includesUnsupervised", "semiML", "unsuperML"]]
    if len(mismatch_semi_unsuper) > 0:
        checked_dict["mismatch_semi_unsuper.tsv"] = mismatch_semi_unsuper

    return checked_dict

def check_rule_logic_vars(reviews):
    # if "ruleML" is true, then "includesRuleBased" must also be true
    # not necessarily the other way around, as a paper can include a rule-based classification of moral values (includesRuleBased) but not necessarily include experiments (ruleML) (but for example just an analysis, as in icwsm_MejovaKM23.json)
    # same check for "logicML" and "includesLogicBased"

    checked_dict = {}

    mismatch_ruleML = reviews[(~reviews["ruleML"].isna() & ~reviews["includesRuleBased"])][["title", "ruleML", "experiment", "includesRuleBased"]]
    if len(mismatch_ruleML) > 0:
        checked_dict["mismatch_ruleML.tsv"] = mismatch_ruleML

    mismatch_logicML = reviews[(~reviews["logicML"].isna() & ~reviews["includesLogicBased"])][["title", "logicML", "experiment", "includesLogicBased"]]
    if len(mismatch_logicML) > 0:
        checked_dict["mismatch_logicML.tsv"] = mismatch_logicML

    return checked_dict

def consistency_checks(only_relevant):

    non_empty_checks = {}
    # A typeResource paper should have resource=resourceYes
    # Same thing for typeExperiment and experimentYes,
    # typeAnalysis and analysisYes,
    not_matching_radios = check_type_radio(only_relevant)
    if len(not_matching_radios) > 0:
        non_empty_checks.update(not_matching_radios)

    not_including_contributions = check_type_contributions(only_relevant)
    if len(not_including_contributions) > 0:
        non_empty_checks.update(not_including_contributions)
    
    # content length should be lower or equal total length
    missing_or_wrong_length = check_length(only_relevant)
    if len(missing_or_wrong_length) > 0:
        non_empty_checks.update(missing_or_wrong_length)
    
    # one of langEn, langOther or langNotSpecified must have a value
    lang_problems = check_lang(only_relevant)
    if len(lang_problems) > 0:
        non_empty_checks.update(lang_problems)

    # if dataSM has a value, then one of dataSMTwitter, dataSMReddit, dataSMFacebook or dataSMOther must have a value
    checked_dataSM = check_dataSM(only_relevant)
    if len(checked_dataSM) > 0:
        non_empty_checks.update(checked_dataSM)
      
    # check if corresponding text boxes were filled for "...Other" variables
    # theoryOtherText and theoryOwnText cannot contain the strings "RoT" or "Thumb".
    missing_text_fields = check_text_fields(only_relevant)
    if len(missing_text_fields) > 0:
        non_empty_checks.update(missing_text_fields)
    
    # resourceYes: all variables must have a value (cannot be empty)
    # experimentsYes: all variables must have a value (cannot be empty)
    # Replicability & Validation: all variables must have a value (cannot be empty)
    # if "includesSupervised" is true, "expLlm" cannot be the only variable with a value in "Which method has been used?" 
    # if "expTransformers" is true, then "includesSupervised" must also be true
    # if "includesUnsupervised" is true and "experimentYes" then either "semiML" or "unsuperML" must be true
    missing_var_values = check_vars_have_values(only_relevant)
    if len(missing_var_values) > 0:
        non_empty_checks.update(missing_var_values)
    
    # "ruleML" and "includesRuleBased" must both be true or false, not one true and one false
    # "logicML" and "includesLogicBased" also
    mismatching_exp = check_rule_logic_vars(only_relevant)
    if len(mismatching_exp) > 0:
        non_empty_checks.update(mismatching_exp)
    
    outfolder = "consistency_checks/"
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    for k, v in non_empty_checks.items():
        with open(outfolder + k, "w") as outf:
            v.to_csv(outf, sep="\t")

    return non_empty_checks

if __name__ == '__main__':
    
    config_parser = configparser.ConfigParser()
    config_parser.read(sys.argv[1])

    review_folder_relpath = config_parser["I/O"]["review_folder_relpath"]
    reviews = survey_utils.read_reviews(review_folder_relpath)

    only_relevant = survey_utils.keep_only_relevant(reviews)

    survey_utils.process_data_info(only_relevant)

    consistency_checks(only_relevant)
    print("")