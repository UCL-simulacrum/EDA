import os
import pandas as pd

default_folder="simulacrum_release_v1.1.0"
    
zlookup_table_names = [
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
    
def make_zlookup_csvs_from_sql(read_folder=default_folder,
                               write_folder=default_folder):
    for table_name in zlookup_table_names:
        read_path = os.path.join(read_folder, "insert_lookups_z" + table_name.lower() + ".sql")
        write_path = os.path.join(read_folder, "insert_lookups_z" + table_name.lower() + ".csv")
        with open(read_path, "r") as read_file:
            lines = read_file.readlines()
            csv = lines[-1].split(' ')[3][1:-1] + "\n"
            for line in lines[2:]:
                values = line.split(' values ')[-1]
                values = values.replace("to_date(", "")
                values = values.replace(",'YYYY-MM-DD')", "")
                csv = csv + values[1:-3] + "\n"
        with open(write_path, "w") as write_file:
            write_file.write(csv)

def load_zlookup_table(table_name,
                       folder=default_folder):           
    read_path = os.path.join(folder, "insert_lookups_z" + table_name.lower() + ".csv")
    table = pd.read_csv(read_path, quotechar="'").set_index("Z"+table_name.upper()+"ID", drop=True)  
    return table

def load_zlookup_tables(table_names=zlookup_table_names,
                        folder=default_folder):
    zlookup_tables = {}
    for table_name in table_names:
        zlookup_tables[table_name] = load_zlookup_table(table_name, folder)
    return zlookup_tables    
    
def get_descriptions(codes, zlookup, folder=default_folder):
    
    unsuitable_zlookups = ['histologylookup', 'icdclassification']
    #check inputs are valid
    if not zlookup.lower() in zlookup_table_names:
        raise ValueError("zlookup must be in " + str(zlookup_table_names))
    if zlookup.lower()=='histologylookup':
        raise ValueError("can't use this funciton for histology use specialised function instead.")
    if zlookup.lower()=='icdclassification':
        raise ValueError("this function won't work for icdclassification. did you want icd?")
        
    zlookup_table = load_zlookup_table(zlookup, folder)
    return pd.Series(codes).map(zlookup_table["SHORTDESC"])

def add_descriptions(table, columns, zlookups, new_names, folder=default_folder):
    
    """This will create new columns in table with names new_names
    based on columns columns translated with zlookups shortdesc.
    
    It won't warn you if your chosen zlookups are wrong. Also some 
    zlookups aren't suitable for use with this.
    
    It is recommended to just use add_descriptions_av_patient and 
    add_descriptions_av_tumour with their default values.
    """

    #check inputs are valid
    if (len(zlookups)!=len(columns) or len(new_names)!=len(columns)):
        raise ValueError("must have same number of columns, zlookups and new_names")
    if not all([name.lower() in zlookup_table_names for name in zlookups]):
        raise ValueError("zlookups must be in " + str(zlookup_table_names))
    if any([name.lower()=='histologylookup' for name in zlookups]):
        raise ValueError("can't use this funciton for histology use specialised function instead.")
    if any([name.lower()=='icdclassification' for name in zlookups]):
        raise ValueError("this function won't work for icdclassification. did you want icd?")
    if not all([column in table.columns for column in columns]):
        raise ValueError("columns must be in " + str(table.columns))
    
    for i in range(len(columns)):
        zlookup_table = load_zlookup_table(zlookups[i], folder)
        table[new_names[i]] = table[columns[i]].map(zlookup_table["SHORTDESC"])
        
    return table

def add_descriptions_av_patient(table,
                                folder=default_folder,
                                columns=["SEX",
                                         "ETHNICITY",
                                         "DEATHLOCATIONCODE",
                                         "NEWVITALSTATUS"],
                                new_names=["SEX_DESC",
                                           "ETHNICITY_DESC", 
                                           "DEATHLOCATIONCODE_DESC",
                                           "NEWVITALSTATUS_DESC"]):
    zlookup_dict = {"SEX":"SEX",
                    "ETHNICITY":"ETHNICITY",
                    "DEATHLOCATIONCODE":"DEATHLOCATION",
                    "NEWVITALSTATUS":"VITALSTATUS"}    
    if not all([column in zlookup_dict.keys() for column in columns]):
        raise ValueError("columns must be in " + str(zlookup_dict.keys())
                         + ". Use specialised function for death cause codes.")    
    zlookups = [zlookup_dict[column] for column in columns]
    return add_descriptions(table, columns, zlookups, new_names, folder=folder)

def add_descriptions_av_tumour(table,
                               folder=default_folder,
                               columns=["SITE_ICD10_O2",
                                        "SITE_ICD10_O2_3CHAR",
                                        "BEHAVIOUR_ICD10_O2",
                                        "STAGE_BEST",
                                        "GRADE",
                                        "SEX",
                                        "CANCERCAREPLANINTENT",
                                        "LATERALITY"],
                               new_names=["SITE_ICD10_O2_DESC",
                                         "SITE_ICD10_O2_3CHAR_DESC",
                                         "BEHAVIOUR_ICD10_O2_DESC",
                                         "STAGE_BEST_DESC",
                                         "GRADE_DESC",
                                         "SEX_DESC",
                                         "CANCERCAREPLANINTENT_DESC",
                                         "LATERALITY_DESC"]):
    zlookup_dict = {"SITE_ICD10_O2":"ICD",
                    "SITE_ICD10_O2_3CHAR":"ICD",
                    "BEHAVIOUR_ICD10_O2":"BEHAVIOUR",
                    "STAGE_BEST":"STAGE",
                    "GRADE":"GRADE",
                    "SEX":"SEX",
                    "CANCERCAREPLANINTENT":"CANCERCAREPLANINTENT",
                    "LATERALITY":"LATERALITY"}
    if not all([column in zlookup_dict.keys() for column in columns]):
        raise ValueError("columns must be in " + str(zlookup_dict.keys())
                         + ". Use specialised functions for morphology and histology. \
                         Descriptions not available for other columns.")
    zlookups = [zlookup_dict[column] for column in columns]
    return add_descriptions(table, columns, zlookups, new_names, folder=folder)

def add_histology_description(table,
                  new_names=["HISTOLOGYID", "HISTOLOGYDESC"],
                  folder=default_folder):
    if not all([column in table.columns for column in ["MORPH_ICD10_O2", "BEHAVIOUR_ICD10_O2"]]):
        raise ValueError("table must include columns MORPH_ICD10_O2 and BEHAVIOUR_ICD10_O2")
    zlookup_table = load_zlookup_table('histologylookup', folder=folder)    
    merged = pd.merge(table[["MORPH_ICD10_O2", "BEHAVIOUR_ICD10_O2"]],
                      zlookup_table.astype(object),
                      how='left',              
                      left_on=["MORPH_ICD10_O2", "BEHAVIOUR_ICD10_O2"],
                      right_on=["ZMORPHOLOGYID", "ZBEHAVIOURID"])
    table["HISTOLOGY_DESC"] = merged["DESCRIPTION"]
    return table