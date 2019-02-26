"""
module for loading the tables
Version 1.1.0
for use with simulacrum_release_v1.1.0
"""

import os
import pandas as pd

default_folder="simulacrum_release_v1.1.0"
default_prefix="sim_"
    
table_names = [
    'av_patient',
    'av_tumour',
    'sact_cycle',
    'sact_drug_detail',
    'sact_outcome',
    'sact_patient',
    'sact_regimen',
    'sact_tumour',
]

def load_table(table_name,
               add_descriptions=False,
               folder=default_folder,
               prefix=default_prefix):
    """
    Loads specified table and returns it.
    
    Option to add all available descriptions.
    """
    read_path = os.path.join(folder, prefix + table_name.lower() + ".csv")
    try:
        table = pd.read_csv(read_path, quotechar='"', dtype=object)
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
                                            add_descriptions=add_descriptions,
                                            folder=folder,
                                            prefix=prefix)
    return table_dict
