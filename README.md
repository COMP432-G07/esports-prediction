# COMP 432

# Authors

- Benjamin Lofo Follo 
- Arman Jahanpour
- Roshleen Mand
- Jialin Yang
# Introduction

## Purpose

This repository holds the code related to the study compiled in the 2021 report *Predictive Analysis in League of Legends e-Sports Matches*, written by the same authors towards the requirements of the COMP 432 Machine Learning class, given to students at Concordia University Montreal's Fall 2021 semester. 

## Deliverable Contents

The deliverable collection contains the following documents:

**Folders**
- `data/`: Resources and files stored from the scripts for data collection
- `data/json`: Example Endpoint Responses for the Riot API that are analyzed by `extract_game_data.py`
- `data/processed`: Final CSV training data set
- `data/raw`: Unprocessed files created by `extract_game_data.py`
- `data/csv`: List of match ids generated by `fetch_game_ids.py`
- `src/`: Executable Python files
- `src/models/`: Joblib files for the models that have been trained by our ipynb file
- `src/parsers/`: Parsers used within `extract_game_data.py` to prepare digestable tuple instances
- `src/services/`: API scripts to communicate with third-party data services

**Files**
- `src/fetch_game_ids.py`: Connects to the Riot API to get all game ids from the available tiers and divisions.
- `src/extract_game_data.py`: Scans all `.csv` files inside the output folder, and calls the Riot API to fetch all information related to each match ids, which includes overall game statistics and game timeline.
- `src/processing.ipynb`: Interactive Jupyter Notebook used to Preprocess the data collected inside the `data` folder.
- `src/training.ipynb`: Interactive Jupyter Notebook used to train models against the preprocessed data inside the `data` folder.
  
# Requirements

The following packages are required to ensure all scripts run properly
- sklearn: Provides k-Means library for clustering and vectorizing text
- os: Read the files in the folder specified
  
A Riot API key is also needed for the API Client to work, which you can get here: https://developer.riotgames.com/
# Instructions


1. Fetch the game ids with the following command
```
$ python src/fetch_game_ids.py
```

2. Extract the game data using the following command **(NOTE: this step may take very long (ETA:20 hours)**
```
$ python src/extract_game_data.py
```

3. Run the `processing.ipynb` to pre-process the data prior to analysis
4. Use the `training.ipynb` file to train the machine learning models

# Thank you

We have used these sources for bringing the project to life:

*AlphaStar: Grandmaster level in StarCraft II using multi-agent reinforcement learning* (For formatting layout of our report)
https://deepmind.com/blog/article/AlphaStar-Grandmaster-level-in-StarCraft-II-using-multi-agent-reinforcement-learning

*Riot Developer - Collecting data* (Best practices on the Riot API)
https://riot-api-libraries.readthedocs.io/en/latest/collectingdata.html

