"""
module for loading the tables
Version 1.1.0
for use with simulacrum_release_v1.1.0
"""

import os
import pandas as pd

default_folder="../simulacrum_release_v1.1.0"
default_prefix="sim_"

table_names = [
    'av_patient',
    'av_tumour',
    'sact_cycle',
    'sact_drug_detail',
    'sact_outcome',
    'sact_patient',
    'sact_regimen',
    'sact_tumour'
]

def load_table(table_name,
               dtype=None,
               parse_dates=None,
               add_descriptions=False,
               folder=default_folder,
               prefix=default_prefix):
    """
    Loads specified table and returns it.

    For the standard tables loads them with recommended types for each column.

    Option to add all available descriptions.
    """

    default_dtypes = {
        'av_patient' : {
            'PATIENTID' : int,
            'SEX' : 'category',
            'LINKNUMBER' : int,
            'ETHNICITY' : 'category',
            'DEATHCAUSECODE_1A' : object,
            'DEATHCAUSECODE_1B' : object,
            'DEATHCAUSECODE_1C' : object,
            'DEATHCAUSECODE_2' : object,
            'DEATHCAUSECODE_UNDERLYING' : object,
            'DEATHLOCATIONCODE' : 'category',
            'NEWVITALSTATUS' : 'category',
            'VITALSTATUSDATE': object
        },
        'av_tumour' : {
            'TUMOURID' : int,
            'PATIENTID' : int,
            'DIAGNOSISDATEBEST' : object,
            'SITE_ICD10_O2' : 'category',
            'SITE_ICD10_O2_3CHAR' : 'category',
            'MORPH_ICD10_O2' : 'category',
            'BEHAVIOUR_ICD10_O2' : 'category',
            'T_BEST' : 'category',
            'N_BEST' : 'category',
            'M_BEST' : 'category',
            'STAGE_BEST' : 'category',
            'STAGE_BEST_SYSTEM' : 'category',
            'GRADE' : 'category',
            'AGE' : float,
            'SEX' : 'category',
            'CREG_CODE' : 'category',
            'LINK_NUMBER' : int,
            'SCREENINGSTATUSFULL_CODE' : 'category',
            'ER_STATUS' : 'category',
            'ER_SCORE' : 'category',
            'PR_STATUS' : 'category',
            'PR_SCORE' : 'category',
            'HER2_STATUS' : 'category',
            'CANCERCAREPLANINTENT' : 'category',
            'PERFORMANCESTATUS' : 'category',
            'CNS' : 'category',
            'ACE27' : 'category',
            'GLEASON_PRIMARY' : 'category',
            'GLEASON_SECONDARY' : 'category',
            'GLEASON_TERTIARY' : 'category',
            'GLEASON_COMBINED' : 'category',
            'DATE_FIRST_SURGERY' : object,
            'LATERALITY' : 'category',
            'QUINTILE_2015' : 'category'
        },
        'sact_cycle' : {
            'MERGED_CYCLE_ID' : int,
            'MERGED_REGIMEN_ID' : int,
            'CYCLE_NUMBER' : int,
            'START_DATE_OF_CYCLE' : object,
            'OPCS_PROCUREMENT_CODE' : 'category',
            'PERF_STATUS_START_OF_CYCLE' : 'category',
            'MERGED_PATIENT_ID' : int,
            'MERGED_TUMOUR_ID' : int
        },
        'sact_drug_detail' : {
            'MERGED_DRUG_DETAIL_ID' : int,
            'MERGED_CYCLE_ID' : int,
            'ORG_CODE_OF_DRUG_PROVIDER' : 'category',
            'ACTUAL_DOSE_PER_ADMINISTRATION' : float,
            'OPCS_DELIVERY_CODE' : 'category',
            'ADMINISTRATION_ROUTE' : 'category',
            'ADMINISTRATION_DATE' : object,
            'DRUG_GROUP' : 'category',
            'MERGED_PATIENT_ID' : int,
            'MERGED_TUMOUR_ID' : int,
            'MERGED_REGIMEN_ID' : int
        },
        'sact_outcome' : {
            'MERGED_OUTCOME_ID' : int,
            'MERGED_REGIMEN_ID' : int,
            'DATE_OF_FINAL_TREATMENT' : object,
            'REGIMEN_MOD_DOSE_REDUCTION' : 'category',
            'REGIMEN_MOD_TIME_DELAY' : 'category',
            'REGIMEN_MOD_STOPPED_EARLY' : 'category',
            'REGIMEN_OUTCOME_SUMMARY' : 'category',
            'MERGED_PATIENT_ID' : int,
            'MERGED_TUMOUR_ID' : int
        },
        'sact_patient' : {
            'MERGED_PATIENT_ID' : int,
            'LINK_NUMBER' : int
        },
        'sact_regimen' : {
            'MERGED_REGIMEN_ID' : int,
            'MERGED_TUMOUR_ID' : int,
            'HEIGHT_AT_START_OF_REGIMEN' : float,
            'WEIGHT_AT_START_OF_REGIMEN' : float,
            'INTENT_OF_TREATMENT' : 'category',
            'DATE_DECISION_TO_TREAT' : object,
            'START_DATE_OF_REGIMEN' : object,
            'MAPPED_REGIMEN' : object,
            'CLINICAL_TRIAL' : 'category',
            'CHEMO_RADIATION' : 'category',
            'MERGED_PATIENT_ID' : int,
            'BENCHMARK_GROUP' : 'category'
        },
        'sact_tumour' : {
            'MERGED_TUMOUR_ID' : int,
            'MERGED_PATIENT_ID' : int,
            'CONSULTANT_SPECIALITY_CODE' : 'category',
            'PRIMARY_DIAGNOSIS' : 'category',
            'MORPHOLOGY_CLEAN' : 'category'
        }
    }
    default_dates = {
        'av_patient' : ['VITALSTATUSDATE'],
        'av_tumour' : ['DIAGNOSISDATEBEST', 'DATE_FIRST_SURGERY'],
        'sact_cycle' : ['START_DATE_OF_CYCLE'],
        'sact_drug_detail' : ['ADMINISTRATION_DATE'],
        'sact_outcome' : ['DATE_OF_FINAL_TREATMENT'],
        'sact_patient' : [],
        'sact_regimen' : ['DATE_DECISION_TO_TREAT', 'START_DATE_OF_REGIMEN'],
        'sact_tumour' : []
    }

    # set to defaults
    table_name = table_name.lower()
    if table_name in table_names:
        if dtype==None:
            dtype=default_dtypes[table_name]
        if parse_dates==None:
            parse_dates=default_dates[table_name]

    read_path = os.path.join(folder, prefix + table_name.lower() + ".csv")
    try:
        table = pd.read_csv(read_path, quotechar='"', dtype=dtype, parse_dates=parse_dates)
    except FileNotFoundError:
        raise ValueError("The file " + read_path + " does not exist.")
    if add_descriptions:
        import descriptions
        table = descriptions.add_descriptions(table, table_name)
    return table

def all_tables(add_descriptions=False,
               folder=default_folder,
               prefix=default_prefix):
    """
    Loads all tables into dictionary with table names as keys.

    Option to add all available descriptions.
    """
    table_dict = {}
    for table_name in table_names:
        table_dict[table_name] = load_table(table_name,
                                            dtype=None,
                                            parse_dates=None,
                                            add_descriptions=add_descriptions,
                                            folder=folder,
                                            prefix=prefix)
    return table_dict
