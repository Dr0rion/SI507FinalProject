#Name: Vardh Jain
#Unique ID: vardhj

#Title: SI507 Final Project - 'FitStroke' 

#Import necessary packages
import requests, json
import pprint as pp
import datetime
import json
import csv
import time
import plotly.graph_objects as go

api_cache = {}
url = "https://api.fitbit.com/1/user/-/profile.json"

def get_cached_data(key, cache_duration):
    """
    Retrieve data from the cache if it has not expired.

    Args:
        key (str): The key to retrieve the data from the cache.
        cache_duration (int): The duration of time (in seconds) before the cache expires.

    Returns:
        The cached data if it exists and has not expired, or None otherwise.
    """
    data = api_cache.get(key)
    if data:
        timestamp, value = data
        # Check if the cache has expired (e.g., after 1 hour or 3600 seconds)
        if time.time() - timestamp < cache_duration:
            return value
    return None

def store_data_in_cache(key, value):
    """
    Store data in the cache with the specified key.

    Args:
        key (str): The key to use when storing the data in the cache.
        value: The value to store in the cache.
    """
    api_cache[key] = (time.time(), value)

def save_cache_to_file(file_path):
    """
    Save the cache to a JSON file.

    Args:
        file_path (str): The path to the file where the cache will be saved.
    """
    with open(file_path, 'w') as cache_file:
        json.dump(api_cache, cache_file, indent=4)

def load_cache_from_file(file_path):
    """
    Load the cache from a JSON file.

    Args:
        file_path (str): The path to the file where the cache is stored.
    """
    global api_cache
    with open(file_path, 'r') as cache_file:
        api_cache = json.load(cache_file)

def get_data_from_api(url, access_token):
    """
    Fetch data from an API endpoint using the provided access token.

    Args:
        url (str): The URL of the API endpoint to fetch data from.
        access_token (str): The access token to use for authentication.

    Returns:
        The data retrieved from the API endpoint.
    """
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
    else:
        print("Failed to fetch user profile data.")

    # remaining_calls = int(response.headers.get('X-RateLimit-Remaining', 0))
    # print(f"Remaining API calls: {remaining_calls}")

    return data

def get_data(url, access_token, cache_duration=3600):
    """
    Retrieve data from the cache if it exists and has not expired,
    or fetch it from the API and store it in the cache.

    Args:
        url (str): The URL of the API endpoint to fetch data from.
        access_token (str): The access token to use for authentication.
        cache_duration (int): The duration of time (in seconds) before the cache expires.

    Returns:
        The cached data if it exists and has not expired, or the data retrieved from the API.
    """
    current_timestamp = int(time.time() // cache_duration)
    cache_key = f"{access_token} - {url} - {current_timestamp}"
    cached_data = get_cached_data(cache_key, cache_duration)

    if cached_data:
        # print("Using cached data")
        return cached_data
    else:
        # print("Fetching data from API")
        data = get_data_from_api(url, access_token)
        store_data_in_cache(cache_key, data)
        return data

def get_daily_steps(date, access_token):
    """
    Retrieves the daily step count for a given date from the Fitbit API.

    Args:
        date (str): The date for which to retrieve the step count in the format YYYY-MM-DD.
        access_token (str): The access token for authenticating with the Fitbit API.

    Returns:
        dict: A dictionary containing the daily step count data for the given date.
    """
    url = f"https://api.fitbit.com/1/user/-/activities/steps/date/{date}/1d.json"
    return get_data(url, access_token)

def get_heart_rate(date, access_token):
    """
    Retrieves the heart rate data for a given date from the Fitbit API.

    Args:
        date (str): The date for which to retrieve the heart rate data in the format YYYY-MM-DD.
        access_token (str): The access token for authenticating with the Fitbit API.

    Returns:
        dict: A dictionary containing the heart rate data for the given date.
    """
    url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1min.json"
    return get_data(url, access_token)

def get_sleep_data(date, access_token):
    """
    Retrieves the sleep data for a given date from the Fitbit API.

    Args:
        date (str): The date for which to retrieve the sleep data in the format YYYY-MM-DD.
        access_token (str): The access token for authenticating with the Fitbit API.

    Returns:
        dict: A dictionary containing the sleep data for the given date.
    """
    url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"
    return get_data(url, access_token)

def get_daily_activity_summary(date, access_token):
    """
    Retrieves the daily activity summary for a given date from the Fitbit API.

    Args:
        date (str): The date for which to retrieve the activity summary in the format YYYY-MM-DD.
        access_token (str): The access token for authenticating with the Fitbit API.

    Returns:
        dict: A dictionary containing the daily activity summary data for the given date.
    """
    url = f"https://api.fitbit.com/1/user/-/activities/date/{date}.json"
    return get_data(url, access_token)

def load_fitbit_data(access_token, today):
    """
    Loads Fitbit data for a given access token and date.

    Parameters:
        access_token (str): The user's access token for the Fitbit API.
        today (str): The date in the format "yyyy-mm-dd" for which the data should be retrieved.

    Returns:
        tuple: A tuple of the retrieved data for the user's profile, daily steps, heart rate, sleep, and activity summary.
    """
    data = get_data(url, access_token)
    steps_data = get_daily_steps(today, access_token)
    heart_rate_data = get_heart_rate(today, access_token)
    sleep_data = get_sleep_data(today, access_token)
    activity_summary = get_daily_activity_summary(today, access_token)

    return data, steps_data, heart_rate_data, sleep_data, activity_summary

def get_user_health_data(steps_data, heart_rate_data, sleep_data, activity_summary):
    """Extracts health data from Fitbit data.

    Parameters:
        steps_data (dict): A dictionary containing the user's daily steps data.
        heart_rate_data (dict): A dictionary containing the user's heart rate data.
        sleep_data (dict): A dictionary containing the user's sleep data.
        activity_summary (dict): A dictionary containing the user's daily activity summary.

    Returns:
        tuple: A tuple containing the user's daily steps, resting heart rate, daily sleep hours, and daily activity levels.
    """
    try:
        steps = int(steps_data["activities-steps"][0]["value"])
        heart_rate = heart_rate_data["activities-heart"][0]["value"]["restingHeartRate"]
        sleep_hours = sleep_data["summary"]["totalMinutesAsleep"] / 60
        activity_levels = activity_summary["goals"]["activeMinutes"]
    except:
        steps = 10000
        heart_rate = 64
        sleep_hours = 7
        activity_levels = 60

    return steps, heart_rate, sleep_hours, activity_levels

def calculate_stroke_risk(steps, heart_rate, sleep, activity_levels):
    """Calculates the user's stroke risk score based on their daily steps, resting heart rate,
    daily sleep duration, and daily active minutes.

    Args:
        steps (int): The user's daily steps count.
        heart_rate (int): The user's resting heart rate.
        sleep (float): The user's daily sleep duration in hours.
        activity_levels (int): The user's daily active minutes.

    Returns:
        int: The user's stroke risk score.
    """
    risk_score = 0

    # Steps (assuming daily steps)
    if steps < 5000:
        risk_score += 2
    elif 5000 <= steps < 10000:
        risk_score += 1
    else:
        risk_score += 0

    # Heart rate (assuming resting heart rate)
    if heart_rate > 100:
        risk_score += 2
    elif 60 <= heart_rate <= 100:
        risk_score += 1
    else:
        risk_score += 0

    # Sleep (assuming daily sleep duration in hours)
    if sleep < 6:
        risk_score += 2
    elif 6 <= sleep <= 9:
        risk_score += 1
    else:
        risk_score += 0

    # Activity levels (assuming daily active minutes)
    if activity_levels < 30:
        risk_score += 2
    elif 30 <= activity_levels < 60:
        risk_score += 1
    else:
        risk_score += 0

    return risk_score


def load_location_mortality_rates(csv_file_path):
    """Loads the stroke mortality rates for specific counties in the states of Michigan, Ohio,
    Indiana, Missouri, and Illinois from a CSV file.

    Args:
        csv_file_path (str): The file path of the CSV file containing the stroke mortality rates.

    Returns:
        dict: A dictionary with county names as keys and mortality rates as values.
    """
    location_mortality_rates = {}

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            state_code = row['LocationAbbr']
            state_names = row['LocationDesc']
            if row['Stratification1'] == row['Stratification2'] == 'Overall':
                if state_names == 'Michigan' or state_names == 'Ohio' or state_names == 'Indiana' or state_names == 'Missouri' or state_names == 'Illinois':
                    location_name = row['LocationDesc']
                    mortality_rate = row['Data_Value']
                    if mortality_rate:
                        location_mortality_rates[location_name] = mortality_rate
                elif state_code == 'MI' and state_names != 'Michigan':
                    location_name = row['LocationDesc']
                    mortality_rate = row['Data_Value']
                    if mortality_rate:
                        location_mortality_rates[location_name] = mortality_rate
    return location_mortality_rates

def calculate_personalized_mortality_rate(user_risk, min_risk, max_risk, min_mortality, max_mortality):
    """
    Calculates the user's personalized mortality rate based on their risk score.

    Parameters:
    user_risk (float): The user's risk score.
    min_risk (float): The minimum risk score in the dataset.
    max_risk (float): The maximum risk score in the dataset.
    min_mortality (float): The minimum mortality rate in the dataset.
    max_mortality (float): The maximum mortality rate in the dataset.

    Returns:
    float: The user's personalized mortality rate.
    """
    normalized_risk = (user_risk - min_risk) / (max_risk - min_risk)

    user_mortality_rate = min_mortality + normalized_risk * (max_mortality - min_mortality)

    return user_mortality_rate

def find_min_max_mortality_rates(mortality_rates):
    """
    Finds the minimum and maximum mortality rates in the given mortality rates dictionary.

    Parameters:
    mortality_rates (dict): A dictionary of county names as keys and mortality rates as values.

    Returns:
    tuple: A tuple containing the minimum and maximum mortality rates.
    """
    min_mortality_rate = min(float(value) for value in mortality_rates.values())
    max_mortality_rate = max(float(value) for value in mortality_rates.values())

    return min_mortality_rate, max_mortality_rate


def get_mortality_rate(location, mortality_rates):
    """
    Returns the mortality rate based on the user's location.

    Parameters:
    location (str): The user's location.
    mortality_rates (dict): A dictionary of county names as keys and mortality rates as values.

    Returns:
    float: The mortality rate based on the user's location.
    """
    if location in mortality_rates:    
        return mortality_rates[location]
    elif location == 'Michigan County':
        return mortality_rates['Michigan']
    else:
        return mortality_rates['Michigan']

def compare_health_data(risk_score, mortality_rate):
    """
    Compares the user's health data with the regional stroke mortality data and returns a list of results.

    Args:
    risk_score (int): The user's calculated stroke risk score.
    mortality_rate (float): The mortality rate for the user's region.

    Returns:
    list: A list containing the user's risk level (Low, Moderate, High, or Very High) and their personalized mortality rate.
    """
    if risk_score <= 2:
        risk_level = "Low"
    elif 2 < risk_score <= 5:
        risk_level = "Moderate"
    elif 5 < risk_score <= 8:
        risk_level = "High"
    else:
        risk_level = "Very High"
    
    comparison_result = {
        "risk_level": risk_level,
        "user_mortality_rate": mortality_rate,
    }    
    values_list = []
    for v in comparison_result.values():
        values_list.append(v)

    return values_list

def create_comparison_plot(x, y):
    """
    Creates and displays a bar plot comparing the three different mortality rates

    Args:
    x (list): A list of 3 names - User name, county name, Midwest state
    y (list): A list of 3 stroke mortality rates - User's rate, county's rate, state's rate

    Returns:
    Displays bar plot 
    """
    # Define the colors of the bars
    colors = ['darkorange', 'white', 'green']

    # Create the trace for the bar chart
    trace = go.Bar(x=x, y=y, marker=dict(color=colors))

    # Create the data object and layout object for the plot
    data = [trace]
    layout = go.Layout(
        title='Comparison of Mortality Rates',
        xaxis_title='Rate Types',
        yaxis_title='Stroke Mortality Rates(per 100,000 population)'
        )

    # Create the figure and plot the data
    fig = go.Figure(data=data, layout=layout)
    fig.show()

class TreeNode:
    def __init__(self, data, parent=None):
        self.data = data
        self.parent = parent
        self.children = []

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def __repr__(self, level=0):
        ret = "\t" * level + repr(self.data) + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

    def to_dict(self):
        return {
            'data': self.data,
            'children': [child.to_dict() for child in self.children]
        }

def main():

    print('\nHi, Welcome to FitStroke!\n')
    print('FitStroke asks you to enter your Michigan county location\nand calculates your Stroke Mortality Rate(per 100,000 population).\n')
    print('It then lets you visualise your Stroke Mortality Rate to the rate\nin your Michigan county and a Midwest state of your choice with a barplot.\n')   

    access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1FWWE0iLCJzdWIiOiJCSFI0ODciLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJhY3QgcnNldCBybG9jIHJ3ZWkgcmhyIHJudXQgcnBybyByc2xlIiwiZXhwIjoxNzEyNjM4MzIzLCJpYXQiOjE2ODExMDIzMjN9.tMAFgYZfzlNO_p8eB46tYvVAHrnbGF69Gk-bu32q_0E"
    csv_file_path = '/Users/vardhj/Desktop/Winter2023/SI507/Final Project/SI507FinalProject/Stroke_Mortality_Data.csv'
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Load the cache from the JSON file
    try:
        load_cache_from_file('cache.json')
    except:
        pass

    # Load Fitbit data
    data, steps_data, heart_rate_data, sleep_data, activity_summary = load_fitbit_data(access_token, today)
    user_data = data['user']

    while True:
        start = input('Would you like to try FitStroke (Enter Y/N): ')  
        if start.lower() in ['y', 'yup', 'yes', 'yas', 'yay']:
            print(f"\n{user_data['fullName']}, {user_data['age']} year old, {user_data['gender']}\n")
            break
        elif start.lower() in ['n', 'no', 'nope']: 
            print("\nThank you for using FitStroke!\n")
            exit()
        else:
            print('\nPlease enter Y/N\n')
            continue

    # Save the cache to a JSON file
    save_cache_to_file('cache.json')

    ## Get the user's Fitbit data
    steps, heart_rate, sleep_hours, activity_levels = get_user_health_data(steps_data, heart_rate_data, sleep_data, activity_summary)
    print(f"Your Fitbit Data summary for today is: \nSteps = {steps}\nHeart Rate = {heart_rate} bpm\nHours of Sleep = {sleep_hours}\nMinutes of Activity = {activity_levels}")
    
    # Load mortality rates
    mortality_rates = load_location_mortality_rates(csv_file_path) 

    # Get the user's location
    while True:
        user_location = input("\nEnter the name of your Michigan County: ")
        if user_location:
            found_location = False
            for k in mortality_rates.keys():
                if user_location.lower() in k.lower() and user_location != ' ':
                    user_location = k
                    found_location = True
                    break
            if not found_location:
                print('\nPlease enter a valid Michigan County location.')
                continue
            break
        else:
            print('\nPlease enter a valid Michigan County location.')
            continue

    ## Calculate the user's stroke risk score and personalized mortality rate
    risk_score = calculate_stroke_risk(steps, heart_rate, sleep_hours, activity_levels)
    print(f"\nBased on your Fitbit data, your calculated risk score for Stroke is: {risk_score}\n")

    ## Compare the user's health data with the regional stroke mortality data
    mortality_rate = get_mortality_rate(user_location, mortality_rates)
    comparison_result = compare_health_data(risk_score, mortality_rate)
    print(f"Your risk of developing Stroke is: {comparison_result[0]}\n")

    ## Calculate the user's health data with the regional stroke mortality data
    min_rate, max_rate = find_min_max_mortality_rates(mortality_rates)
    personalized_mortality_rate = calculate_personalized_mortality_rate(risk_score, min_risk=0, max_risk=8, min_mortality=min_rate, max_mortality=max_rate)
    personalized_mortality_rate = round(personalized_mortality_rate, 1)
    print(f"For this score, your Stroke Mortality Rate is: {personalized_mortality_rate}")

    print(f"\nThe stroke mortality rate of {user_location} is: {comparison_result[1]}")

    #Compare to other Midwestern States
    MW_states = {'1.': 'Michigan', 
                 '2.': 'Ohio',
                 '3.': 'Indiana',
                 '4.': 'Illinois',
                 '5.': 'Missouri'}

    state_location = None
    MW_mortality_rate = None
    while True:
        choice_state = input('\nWould you like to compare your stroke mortality rate to different Midwestern States (Enter Y/N): ')
        if choice_state.lower() in ['y', 'yup', 'yes', 'yas', 'yay']:
            for k, v in MW_states.items():
                print(k, v)
            choose_MW_states = input('\nOkay, enter the number to make a choice: ')
            choose_MW_states = choose_MW_states + '.'
            if choose_MW_states in MW_states:
                state_location = MW_states[choose_MW_states]
                MW_mortality_rate = get_mortality_rate(state_location, mortality_rates)
                print(f"\nThe stroke mortality rate of {state_location} is {MW_mortality_rate}")
            else:
                print("\nInvalid choice. Please try again.")
        elif choice_state.lower() in ['n', 'no', 'nope']:
            print("\nThank you for using FitStroke!\n")
            break
        else:
            print('\nPlease enter Y/N')
            continue

    # Create the root node for Fitbit health data
    fitbit_health_root = TreeNode("Fitbit Health Data")

    # Add children for each health metric
    for metric, value in data.items():
        metric_node = TreeNode(f"{metric}: {value}")
        fitbit_health_root.add_child(metric_node)

    # Create the root node for stroke mortality data
    stroke_mortality_root = TreeNode("Stroke Mortality Data")

    # Add children for each location and mortality rate
    for location, rate in mortality_rates.items():
        location_node = TreeNode(f"{location}: {rate}")
        stroke_mortality_root.add_child(location_node)

    # Convert the trees to dictionaries
    fitbit_health_dict = fitbit_health_root.to_dict()
    stroke_mortality_dict = stroke_mortality_root.to_dict()

    # Combine the dictionaries into a single dictionary
    combined_tree = {
    'fitbit_health_data': fitbit_health_dict,
    'stroke_mortality_data': stroke_mortality_dict
    }

    # Save the combined dictionary to a JSON file
    with open('combined_tree.json', 'w') as f:
        json.dump(combined_tree, f, indent = 4)
    
    # Define the x-axis values
    x = [user_data['fullName'], user_location, state_location]

    # Define the y-axis values
    y = [personalized_mortality_rate, comparison_result[1], MW_mortality_rate]

    #Call comparison plot function
    create_comparison_plot(x,y)

if __name__ == "__main__":
    main()



                



