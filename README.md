# Exploration of the Simulacrum Artificial Patient Cancer Data

# Introduction

To give you some context on the work that is done in this repo we have written a report - projectreport.pdf and have made slides from our presentation - presentation.pptx (above).

# Getting Started

## Setting up the repository

Create a directory which will hold your simulacrum project and navigate to it.  

```bash
mkdir simulacrum
cd simulacrum
```

Clone the EDA repository inside your project directory

```bash
git clone git@github.com:UCL-simulacrum/EDA.git
```

## Getting the data

Download and unzip the simulacrum dataset in your project directory (e.g. `./simulacrum/`).  If your operating system is macOS and wget is not installed, you can install it by ```brew install wget``` which uses the [Homebrew](https://brew.sh) package manager for macOS.
 
Note that by specifiying a directory in the unzip function with the -d option, unzip will unpack the contents into that directory.
```
wget https://simulacrum.healthdatainsight.org.uk/releases/simulacrum_release_v1.1.0.zip
unzip simulacrum_release_v1.1.0.zip -d simulacrum_release_v1.1.0
```

Alternatively you can download the data [here](https://simulacrum.healthdatainsight.org.uk/requesting-data/).

**NB** The data should be unzipped into the parent directory of `EDA`. Your directory structure should look something like this:

```
simulacrum
│       
│
└───EDA
│   │   cancerdata_EDA.ipynb
│   │   patientpathways.ipynb
|   |   ...
│   
|
└───simulacrum_release_v1.1.0
    │   create_table_sim_av_patient.sql
    │   create_table_sim_av_tumour.sql
    |   ...
```



## Creating a conda environment
This will create a conda development environment with all the dependencies loaded.

* Update conda and append conda-forge (missingno is not available through default search channel)

```bash
conda update conda
conda config --append channels conda-forge
```

* Now create a conda environment called simulacrum using the environment yaml file for this project.  Note that the environment name "simulacrum" is defined inside the .yml file.  

```bash
conda env create -f environment.yml
```

* Then activate that environment to be in it:

```
source activate simulacrum
```

* Once in that environment, further installs are needed for one of the notebooks:
```bash
pip install keras tensorflow
```

* Start Jupyter

```bash
jupyter notebook
```

# Viewing the Jupyter Notebooks

Suggested viewing order of notebooks (those notebooks with Plotly graphs do not directly render on GitHub, so they can be viewed via nbviewer.jupyter.org):

1. example_sql_queries.ipynb

2. cancerdata_EDA.ipynb (via [nbviewer](https://nbviewer.jupyter.org/github/UCL-simulacrum/EDA/blob/master/cancerdata_EDA.ipynb))

3. sact_regimen_study.ipynb

4. patientpathways.ipynb (via [nbviewer](https://nbviewer.jupyter.org/github/UCL-simulacrum/EDA/blob/master/patientpathways.ipynb))





