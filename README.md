# EDA

# Specification of conda environment

After installation of Anaconda, at your terminal command prompt, first check conda is up to date:
```
conda update conda
```
Append conda-forge to the package channels being searched through.  This is because the "missingno" package is available via conda-forge. We do "append" so that the conda-forge channel is only used when the package is not found via default channels.
```
conda config --append channels conda-forge
```
Now create a conda environment called simulacrum
```
conda create -n simulacrum python=3.7 anaconda pandas plotly missingno
```
Then activate being in that environment:
```
source activate simulacrum
```
After you have navigated to the EDA folder, you can start Jupyter by simply
```
jupyter notebook
```

# Viewing the notebook

plotly doesn't seem to render on github, so view the notebook here:

https://nbviewer.jupyter.org/github/UCL-simulacrum/EDA/blob/master/cancerdata_EDA.ipynb

# Hello, is it me you're looking for?


files and subdirectories where the notebook is:

Simulacrum-data-dictionary.xlsx

cancerdata_EDA.ipynb

lookup_tables

simulacrum_release_v1.1.0

descriptions.py
