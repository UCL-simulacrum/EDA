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
    'icd3char',
    'icdclassification',
    'icdfull',
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
    
    Alternatively, to save time, set columns argument to be only the columns 
    you want descriptions of. (In particular, the deathcausecode columns in 
    av_patient take a long time to run)
    
    If you need something more general use:
      
        table[new_name] = get_description(table[column_name], zlookup)
    
    Modifies the table and also returns it.
    """
    
    zlookup_dicts = { 
        'av_patient': {
            "SEX":"SEX",
            "ETHNICITY":"ETHNICITY",
            "DEATHLOCATIONCODE":"DEATHLOCATION",
            "DEATHCAUSECODE_1A":"DEATHCAUSE",              
            "DEATHCAUSECODE_1B":"DEATHCAUSE",              
            "DEATHCAUSECODE_1C":"DEATHCAUSE",
            "DEATHCAUSECODE_2":"DEATHCAUSE",
            "DEATHCAUSECODE_UNDERLYING":"DEATHCAUSE",
            "NEWVITALSTATUS":"VITALSTATUS"
        },
        'av_tumour':  {
            "SITE_ICD10_O2":"ICDFULL",
            "SITE_ICD10_O2_3CHAR":"ICD3CHAR",
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
            "PRIMARY_DIAGNOSIS":"ICDFULL",
            "MORPHOLOGY_CLEAN":"HISTOLOGY"
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
    
    table_name = table_name.lower()
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
    
    Accepts as special cases histology and deathcause as redirects to 
    get_histology_description_1 and get_deathcause_description
    
    Returns the translated values (does not modify in place).
    """
    
    if zlookup.lower()=='histology':
        return get_histology_description_1(codes, folder, prefix)
    if zlookup.lower()=='deathcause':
        return get_deathcause_description(codes, folder, prefix)
    
    #check inputs are valid
    if zlookup.lower()=='icdclassification':
        raise ValueError("this function won't work for icdclassification. did you want icd?")
    if not zlookup.lower() in zlookup_table_names:
        raise ValueError("zlookup must be in " + str(zlookup_table_names))
          
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
    
    codes = pd.Series(codes).astype(str)
    morphology = codes.str[:4]
    behaviour = codes.str[4:]
    return get_histology_description_2(morphology, behaviour, folder, prefix)

def get_deathcause_description(codes, folder=default_folder, prefix=default_prefix):
     
    """
    Accepts a list or pandas series where each element contains 0, 1, or many
    ICD10 codes, separated by commas.
    
    Returns a pandas series of descriptions separated by semicolons.
    """
    codes = pd.Series(codes).astype(str)
    expanded = codes.str.split(',', expand=True)
    translated = pd.DataFrame()
    for col in expanded.columns:
        translated[col] = get_descriptions(expanded[col], 'icdfull')
    empty = pd.Series(index=codes.index, dtype=object)
    contracted = empty.str.cat(translated, sep=';', na_rep='').str.strip(';')    
    return contracted



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
        raise ValueError("The file " + read_path + " does not exist.")
    return table



def make_zlookup_csvs_from_sql(read_folder="simulacrum_release_v1.1.0",
                               read_prefix="insert_lookups_z",
                               write_folder=default_folder,
                               write_prefix=default_prefix):
    
    """
    simulacrum_release_v1.1.0 doesn't come with lookup tables.
    This code converts the sql files to create them to csv lookup tables.
    The results are included in the github now so you don't need to run it.
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
    
def make_zlookup_icd(read_folder="", read_filename="cod.txt",
                            write_folder=default_folder, write_prefix=default_prefix):
    
    """
    Full icd10 lookup table was generated using this code from 
    a lookup table at http://www.wolfbane.com/icd/icd10h.htm.
    zicd didn't have all the codes.
    The results are included in this github so you don't need to run it.
    """
    
    read_path = os.path.join(read_folder, read_filename) 
    write_path_full = os.path.join(write_folder, write_prefix + "icdfull.csv")
    write_path_3char = os.path.join(write_folder, write_prefix + "icd3char.csv")
    broad_cat, broad_desc, code, desc, code_3char, desc_3char, code_just_3char, desc_just_3char = [], [], [], [], [], [], [], []
    current_broad_cat, current_broad_desc, current_code_3char, current_desc_3char = "", "", "", ""
    with open(read_path, "r") as read_file:
        for linenum, line in enumerate(read_file):
            words = line.split()
            if words[0][0]=='(':
                current_broad_cat = line[1:line.index(')')]
                current_broad_desc = line[line.index(')')+2:]
            else:
                broad_cat.append(current_broad_cat)
                broad_desc.append(current_broad_desc)
                if len(words[0])==3:
                    current_code_3char = words[0]
                    current_desc_3char = ' '.join(words[1:])
                    code_just_3char.append(current_code_3char)
                    desc_just_3char.append(current_desc_3char)
                    code.append(words[0])
                else:
                    code.append(words[0][:3] + words[0][4])
                desc.append(' '.join(words[1:]))
                code_3char.append(current_code_3char)
                desc_3char.append(current_desc_3char)
    df_dict = {'ICD_GROUP':broad_cat,
               'ICD_GROUP_DESC':broad_desc,
               'ZICD3CHARID':code_3char,
               'ICD3CHAR_DESC':desc_3char,
               'ZICDFULLID':code,
               'SHORTDESC':desc}
    df_dict_3char = {'ZICD3CHARID':code_just_3char,
                     'SHORTDESC':desc_just_3char}
    icddf = pd.DataFrame(df_dict)
    icddf3char = pd.DataFrame(df_dict_3char)
    icddf.set_index('ZICDFULLID').to_csv(write_path_full)
    icddf3char.set_index('ZICD3CHARID').to_csv(write_path_3char)
