# FitStroke

This project was implemented as a part of the SI 507 Intermediate Python Programming Course. The FitStroke tool is a Python-based application that processes Fitbit health data and regional stroke mortality rates to provide users with insights about their health and stroke risk compared to regional averages. The dataset has been obained from the Data.gov which is the United States government's open data website and includes Stroke Mortality Rates data based on counties and states in the United States. The dataset along with the visualization can be used for comparing your Stroke Mortality Rate (per 100,000 population) with the rate in your county and a Midwestern State of your choice.

---

## Requirements

- Python 3.6 or higher

## Required Packages

- plotly (version 4.14.3 or higher)
- csv (standard library)
- json (standard library)
- requests (standard library)

To install the required package, run:

```
pip install plotly
```

## Environment
This project was implemented in Visual Studio Code and can be run by typing the command "python SI507_Final_Project.py" in the terminal on opening the .py file. The user must download a copy of the CSV file in the repository and upload into VS code before running the program. Then, it is important for the user to register on the Fitbit API website to get their own Access Key/Token that can be replaced in the .py file in the main() function. It is also important to change the CSV file path in the main() function to the user's file  path of the CSV file.

# User Interaction
On running the .py file, the user will be prompted to enter his Michigan County location. The user can input this through the Visual Studio Code terminal. This will then call the Fitbit API to retreive the user's Fitbit data. Then, the user will be shown his risk score and stroke mortality rate and asked to enter his county location. The user is also given an option to compare these mortality rates to the other Midwestern state rates.

# Data Visualization/Data Structure
If the user decides to exits FitStroke at any time, he will be shown a bar plot comparing the two/three stroke mortality rates. At the back end, a tree data structure has been first generated based on user-inputed values, stored in a .json format, and then converted to a bar plot using plotly.

