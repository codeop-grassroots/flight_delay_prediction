# <center>Flight delay prediction in JFK airport using machine learning classifiers</center>
This repository contains the following files:
- flight_delays.ipynb (notebook of the project)
- JFK_dep_data.csv (dataset containing JFK departures details)
- airports.csv (dataset containing US airports details)
- app.py (application to run with Streamlit in order to visualize the dashboard)
- presentation.pdf (to explain the results of the project)

The main goal of this project is to predict the delays of flights departing from JFK (New York) airport. The delay (in minutes) of every flight will be transformed into a binary target to separate delayed from non-delayed flights, resulting in a supervised classification problem. To assess whether a flight will be delayed or not, several machine learning classifiers will be used. The results will be compared and the best classifier will be chosen to improve its performance by hyperparameter tuning.

The dataset has been obtained from [Kaggle](https://www.kaggle.com/datasets/deepankurk/flight-take-off-data-jfk-airport) and contains the details of flights taking off from JFK airport between November 2019 and January 2020. The coordinates of the destination airports (longitude and latitude) are missing, so they were extracted [from another dataset](https://www.kaggle.com/datasets/usdot/flight-delays?select=airports.csv) in order to do some geographical plots.

The project is divided in 4 parts:
1. An Exploratory Data Analysis (EDA) to summarize and visualize the main charcteristics of the dataset.
2. Compare several classification algorithms (using default parameters) and test different techniques for solving the imbalanced nature of the data (e. g. SMOTE oversampling).
3. Select the best classifying algorithm and improve it by performing hyperparameter optimization.
4. Create a dashboard using [Streamlit](https://streamlit.io/) in order to display the data in a fancy and interactive way and deploy this app in [Heroku](https://www.heroku.com/).

The dashboard can be accessed here: [https://jfkdepartures.herokuapp.com/](https://jfkdepartures.herokuapp.com/)<br>
I hope you like it! 😊