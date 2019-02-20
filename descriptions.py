"""
module for turning codes into human-readable descriptions
Version 1.1.0
for use with simulacrum_release_v1.1.0
"""

import os
import pandas as pd

default_folder="lookup_tables"
default_prefix="z"
    
zlookup_table_names = [
    'ace27score',
    'administrationroute',
    'allred',
    'basis',
    'behaviour',
    'cancercareplanintent',
    'clinicaltrial',
    'cns',
    'consultantspeciality',
    'creg',
    'cnslocation',
    'deathlocation',
    'diagnosticroute',
    'erprstatus',
    'ethnicity',
    'grade',
    'histologylookup',
    'icd',
    'icdclassification',
    'laterality',
    'morphology',
    'performance',
    'regimenintent',
    'regimenoutcome',
    'sex',
    'stage',
    'tnmedition',
    'vitalstatus',
    'yesnounknown'
]



def add_descriptions(table,
                     table_name,
                     columns=None,
                     histology=True,
                     folder=default_folder,
                     prefix=default_prefix,):
    """
    Pass the table and which table it is (e.g. 'av_patient')
    to add all available descriptions to the table.  
    
    Alternatively set columns argument to be only the columns 
    you want descriptions of.
    
    If you need something more general use:
      
        table[new_name] = get_description(table[column_name], zlookup)
    
    Modifies the table and also returns it.
    """
    
    zlookup_dicts = { 
        'av_patient': {
            "SEX":"SEX",
            "ETHNICITY":"ETHNICITY",
            "DEATHLOCATIONCODE":"DEATHLOCATION",
            "NEWVITALSTATUS":"VITALSTATUS"
        },
        'av_tumour':  {
            "SITE_ICD10_O2":"ICD",
            "SITE_ICD10_O2_3CHAR":"ICD",
            "MORPH_ICD10_O2":"MORPHOLOGY",
            "BEHAVIOUR_ICD10_O2":"BEHAVIOUR",
            "STAGE_BEST":"STAGE",
            "GRADE":"GRADE",
            "SEX":"SEX",
            "CREG_CODE":"CREG",
            "ER_STATUS":"ERPRSTATUS",
            "ER_SCORE":"ALLRED",
            "PR_STATUS":"ERPRSTATUS",
            "PR_SCORE":"ALLRED",
            "HER2_STATUS":"ERPRSTATUS",
            "CANCERCAREPLANINTENT":"CANCERCAREPLANINTENT",
            "PERFORMANCESTATUS":"PERFORMANCE",
            "CNS":"CNS",
            "ACE27":"ACE27SCORE",
            "LATERALITY":"LATERALITY"
        },
        'sact_patient': {
        },
        'sact_tumour': {
            "CONSULTANT_SPECIALITY_CODE":"CONSULTANTSPECIALITY",
            "PRIMARY_DIAGNOSIS":"ICD",
            "MORPHOLOGY_CLEAN":"HISTOLOGYLOOKUP"
        },
        'sact_regimen': {
            "INTENT_OF_TREATMENT":"REGIMENINTENT",
            "CLINICAL_TRIAL":"CLINICALTRIAL"
        },
        'sact_outcome': {
            "REGIMEN_OUTCOME_SUMMARY":"REGIMENOUTCOME"
        },
        'sact_cycle': {
            "PERF_STATUS_START_OF_CYCLE":"PERFORMANCE"
        },
        'sact_drug_detail': {
            "ADMINISTRATION_ROUTE":"ADMINISTRATIONROUTE"
        }
    }
    
    try:
        zlookup_dict = zlookup_dicts[table_name]
    except KeyError:
        raise ValueError("table_name must be in " + str(zlookup_dicts.keys()))
    
    if columns == None:
        columns = list(zlookup_dict.keys())
    
    if not all([column in zlookup_dict.keys() for column in columns]):
        raise ValueError("chosen columns must be in " + str(zlookup_dict.keys())
                         + ". Descriptions not available for other columns. \
                         For histology in av_tumour use histology=True. \
                         Can't do OPCS code yet but can apparently be looked up in TRUD")
    if not all ([column in table.columns for column in columns]):
        raise ValueError("the table does not contain those columns. Is table_name correct?")
   
    for column in columns:
        table[column + "_DESC"] = get_descriptions(table[column],
                                                   zlookup_dict[column],
                                                   folder=folder, prefix=prefix)
        
    if table_name == 'av_tumour' and histology:
        table["HISTOLOGY_DESC"] = get_histology_description_2(table["MORPH_ICD10_O2"],
                                                            table["BEHAVIOUR_ICD10_O2"],
                                                            folder=folder,
                                                            prefix=prefix)
    return table





def get_descriptions(codes, zlookup, folder=default_folder, prefix=default_prefix):
    
    """
    Pass a list or pandas series of codes and the zlookup table to translate them with.
    
    Returns the translated values (does not modify in place).
    """
    
    #check inputs are valid
    if zlookup.lower()=='icdclassification':
        raise ValueError("this function won't work for icdclassification. did you want icd?")
    if not zlookup.lower() in zlookup_table_names:
        raise ValueError("zlookup must be in " + str(zlookup_table_names))
        
    if zlookup.lower()=='histologylookup':
        return get_histology_description_1(codes, folder, prefix)
    else:    
        zlookup_table = load_zlookup_table(zlookup, folder, prefix)
        return pd.Series(codes).map(zlookup_table["SHORTDESC"])

    
    
def get_histology_description_2(morphology, behaviour, folder=default_folder, prefix=default_prefix):
    
    """
    Get the histology from two lists or pandas series
    containing morphology and behaviour.
    """
    
    zlookup_table = load_zlookup_table('histologylookup', folder=folder, prefix=prefix)
    df = pd.DataFrame()
    df["ZMORPHOLOGYID"] = morphology
    df["ZBEHAVIOURID"] = behaviour
    merged = pd.merge(df,
                      zlookup_table.astype(object),
                      how='left')
    return merged["DESCRIPTION"]



def get_histology_description_1(codes, folder=default_folder, prefix=default_prefix):
     
    """
    Get the histology from a single list or pandas series 
    containing morphology and behaviour combined.
    """
    
    codes = pd.Series(codes)
    morphology = codes.str[:4]
    behaviour = codes.str[4:]
    return get_histology_description_2(morphology, behaviour, folder, prefix)


def load_zlookup_table(table_name,
                       folder=default_folder,
                       prefix=default_prefix):
    """
    load a lookup table (using just the name, e.g. 'ace27score', 
    not the entire file path)
    """
    read_path = os.path.join(folder, prefix + table_name.lower() + ".csv")
    try:
        table = pd.read_csv(read_path, quotechar='"', dtype=object
                           ).set_index("Z"+table_name.upper()+"ID", drop=True)
    except FileNotFoundError:
        raise ValueError("The file " + read_path + " does not exist. See setup.ipynb")
    return table



def make_zlookup_csvs_from_sql(read_folder="simulacrum_release_v1.1.0",
                               read_prefix="insert_lookups_z",
                               write_folder=default_folder,
                               write_prefix=default_prefix):
    
    """
    simulacrum_release_v1.1.0 doesn't come with lookup tables.
    This code converts the sql files to create them to csv lookup tables.
    The csv files are included in the github now so you won't need to.
    So are some others, mostly taken from https://www.datadictionary.nhs.uk/
    """
    
    sql_names = [
                    'ace27score',
                    'allred',
                    'basis',
                    'behaviour',
                    'cancercareplanintent',
                    'cnslocation',
                    'deathlocation',
                    'diagnosticroute',
                    'ethnicity',
                    'grade',
                    'histologylookup',
                    'icd',
                    'icdclassification',
                    'laterality',
                    'sex',
                    'stage',
                    'tnmedition',
                    'vitalstatus',
                    'yesnounknown'
                ]
    for table_name in sql_names:
        read_path = os.path.join(read_folder, read_prefix + table_name.lower() + ".sql")
        write_path = os.path.join(write_folder, write_prefix + table_name.lower() + ".csv")
        with open(read_path, "r") as read_file:
            lines = read_file.readlines()
            csv = lines[-1].split(' ')[3][1:-1] + "\n"
            for line in lines[2:]:
                values = line.split(' values ')[-1]
                values = values.replace("to_date(", "")
                values = values.replace(",'YYYY-MM-DD')", "")
                csv = csv + values[1:-3] + "\n"
        csv = csv.translate(str.maketrans("'", '"'))
        with open(write_path, "w") as write_file:
            write_file.write(csv)

            
            
def make_zlookup_morphology(read_folder="", read_filename="morph.txt",
                            write_folder=default_folder, write_prefix=default_prefix):
    
    """
    Morphology lookup table was generated using this code from 
    a histology lookup table at http://www.wolfbane.com/icd/icdo2.htm.
    zhistologylookup didn't have well-organised enough descriptions.
    The results are included in this github so you don't need to run it.
    """
    
    read_path = os.path.join(read_folder, read_filename) 
    write_path = os.path.join(write_folder, write_prefix + "morphology.csv")
    broad_cat, broad_desc, morphids, behaviours, hists = [], [], [], [], []
    current_broad_cat, current_broad_desc = "", ""
    with open(read_path, "r") as read_file:
        for linenum, line in enumerate(read_file):
            if line[0]=='(':
                current_broad_cat = line[1:line.index(')')]
                current_broad_desc = line[line.index(')')+2:-1]
            else:
                broad_cat.append(current_broad_cat)
                broad_desc.append(current_broad_desc)
                morphids.append(line[1:5])
                behaviours.append(line[6])
                hists.append(line[8:-1])
    df_dict = {'MORPH_GROUP':broad_cat,
               'MORPH_GROUP_DESC':broad_desc,
               'ZMORPHOLOGYID':morphids,
               'ZBEHAVIOURID':behaviours,
               'DESCRIPTION':hists}
    morphdf = pd.DataFrame(df_dict)
    bad_words = ["benign", "malignant", "metastatic", "NOS", "uncertain", "whether", "or",
             "in", "situ", "borderline", "malignancy"]
    morphdf["SHORTDESC"] = morphdf["DESCRIPTION"].map(
        lambda sentence: ' '.join(filter(
            lambda word: word not in bad_words, sentence.split(' ')
        )).rstrip(',')
    )
    zmorph = morphdf.groupby("ZMORPHOLOGYID")["SHORTDESC"].unique().map(lambda x: '/'.join(x))
    pd.DataFrame(zmorph).to_csv(write_path)
    