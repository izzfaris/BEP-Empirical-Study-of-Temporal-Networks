# BEP-Empirical-Study-of-Temporal-Networks

This a Bachelor's of Data Science End Project at University of Technology Eindhoven and Tilburg University for Izz Faris Ashran (1770608) on Temporal Networks. Supervisors are Dr. George Fletcher and Dr. Nikolay Yakovets.

The Git contains all the code necessary to reproduce the results of the thesis. All the datasets collected are in the `Datasets` folder. They are in `CSV` (Pre-cleaned) and `Pickle` (Cleaned) formats. The plots produced by the code is stored in the `Plots` folder. 

## Table of Contents 
- [Installation](#installation)
- [Features](#features)

## Installation

### Prerequisites
-  Python 3.10+
- pip (Python Package Installer)

### Steps
1. Clone the repository
2. Create a virtual environment
3. Install the required packages in `requirements.txt`

## Features

1. `Data_conversion.py` - This file concatenates each dataframe returned from `Scraper.py` and converts it to a `CSV` file. It can be modified to change what is collected. 
2. `Cleaning.ipynb ` - This cleans both datasets to convert formats, remove null values, etc. Based on Quality Metrics defined in the thesis. The datasets are then saved as `Pickle` files to retain their formatting.
3. `Football.ipynb` - This file loads the cleaned football data and provides some exploratory plots. It also constructs a basic temporal network from the data and runs the `Temporal_Metrics.py` file to calculate the centrality metrics. 
4. `Jets.ipynb` - This does the exact same thing as `Football.ipynb` but for the Private Jet data instead.

### Backend Features
1. `Scraper.py` - This file contains code to scrape data from two websources. 
2. `Temporal_Metrics.py` - The file contains functions to calculate the temporal versions of the basic centralities as well as reachability latency. 
3. `Slice_Plot.py` - This file contains a function that plots the temporal network in a slice plot.
4. `Accuracy.ipynb` - This is used to manually check if the scraped data matches the website values. 