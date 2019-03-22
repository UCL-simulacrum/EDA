# EDA
# Viewing the notebook

plotly doesn't seem to render on github, so view the notebook here:

cancerdata_EDA.ipynb:
https://nbviewer.jupyter.org/github/UCL-simulacrum/EDA/blob/master/cancerdata_EDA.ipynb

patientpathways.ipynb:
https://nbviewer.jupyter.org/github/UCL-simulacrum/EDA/blob/master/patientpathways.ipynb

# Running the Code Locally

#### Setting up the repository

* Create a directory which will hold your simulacrum project and navigate to it.  

```bash
mkdir simulacrum
cd simulacrum
```

* Download and unzip the simulacrum dataset.
```
wget https://simulacrum.healthdatainsight.org.uk/releases/simulacrum_release_v1.1.0.zip
unzip simulacrum_release_v1.1.0.zip
```
* Clone the EDA repository

```bash
git clone git@github.com:UCL-simulacrum/EDA.git
```

#### Creating a conda environment
This will create a conda development environment with all the dependencies loaded.

* Update conda and append conda-forge (missingno is not available through default search channel)

```bash
conda update conda
conda config --append channels conda-forge
```

* Now create a conda environment called simulacrum using the environment yaml file for this project.

```bash
conda env create -n simulacrum environment.yml
```

* Then activate being in that environment:

```bash
conda env activate simulacrum
```

Start Jupyter

```bash
jupyter notebook
```
