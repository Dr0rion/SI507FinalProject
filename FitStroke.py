#Name: Vardh Jain
#Unique ID: vardhj

#Import necessary packages
import os
import requests, json
from requests_oauthlib import OAuth2Session
import pprint as pp
import pandas as pd
import datetime
import json
import csv
import time
import webbrowser

# Implicit Grant Flow
# Get this token from requesting in browser


# authorization_url = 'https://www.fitbit.com/oauth2/authorize?response_type=token&client_id=23QVXM&redirect_uri=http://localhost&scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=31536000'
# webbrowser.open(authorization_url)
# Allow all in the browser and then copy the access_token value from the response URL in the browser. 
# Store the access token in a variable in Python and use it to make requests to the Fitbit API. 

# access_token = input("Enter the access_token from the URL: ")
 


api_cache = {}
print(api_cache)
url = "https://api.fitbit.com/1/user/-/profile.json"

def get_cached_data(key, cache_duration):
    data = api_cache.get(key)
    if data:
        timestamp, value = data
        # Check if the cache has expired (e.g., after 1 hour or 3600 seconds)
        if time.time() - timestamp < cache_duration:
            return value
    return None

def store_data_in_cache(key, value):
    api_cache[key] = (time.time(), value)


def get_data_from_api(url, access_token):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
    else:
        print("Failed to fetch user profile data.")

    remaining_calls = int(response.headers.get('X-RateLimit-Remaining', 0))
    print(f"Remaining API calls: {remaining_calls}")

    return data

def get_data(url, access_token, cache_duration=3600):
    current_timestamp = int(time.time() // cache_duration)
    cache_key = f"{access_token} - {url} - {current_timestamp}"
    cached_data = get_cached_data(cache_key, cache_duration)

    if cached_data:
        print("Using cached data")
        return cached_data
    else:
        print("Fetching data from API")
        data = get_data_from_api(url, access_token)
        store_data_in_cache(cache_key, data)
        return data

def get_daily_steps(date, access_token):
    url = f"https://api.fitbit.com/1/user/-/activities/steps/date/{date}/1d.json"
    return get_data(url, access_token)

def get_intraday_heart_rate(date, access_token):
    url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1min.json"
    return get_data(url, access_token)

def get_sleep_data(date, access_token):
    url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"
    return get_data(url, access_token)

def get_daily_activity_summary(date, access_token):
    url = f"https://api.fitbit.com/1/user/-/activities/date/{date}.json"
    return get_data(url, access_token)


##Print function calls

# pp.pprint(steps_data['activities-steps'][0]['value'])
# pp.pprint(heart_rate_data)
# print(heart_rate_data.keys())
# pp.pprint(sleep_data)
# pp.pprint(activity_summary)


def calculate_stroke_risk(steps, heart_rate, sleep, activity_levels):
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


def load_mortality_rates(csv_file_path):
    mortality_rates = {}

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            location_name = row['LocationDesc']
            mortality_rate = row['Data_Value']
            if mortality_rate:
                mortality_rates[location_name] = mortality_rate
# # A dictionary with county names as keys and mortality rates as values
# pp.pprint(mortality_rates)



# Process the data to calculate the stroke mortality rate for each state/territory and county

def get_mortality_rate(location, mortality_rates):
    # Returns the mortality rate based on the user's location
    if location in mortality_rates:    
        return mortality_rates[location]
    else:
        # Return the national average if the location is not available
        national_average = sum(mortality_rates.values()) / len(mortality_rates)
        return national_average

def compare_health_data(risk_score, mortality_rate):
    # Compares the user's health data with the regional stroke mortality data
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
    
    return comparison_result

def main():

    access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1FWWE0iLCJzdWIiOiJCSFI0ODciLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJhY3QgcnNldCBybG9jIHJ3ZWkgcmhyIHJudXQgcnBybyByc2xlIiwiZXhwIjoxNzEyNjM4MzIzLCJpYXQiOjE2ODExMDIzMjN9.tMAFgYZfzlNO_p8eB46tYvVAHrnbGF69Gk-bu32q_0E"
    csv_file_path = '/Users/vardhj/Desktop/Winter2023/SI507/Final Project/Stroke_Mortality_Data.csv'


    today = datetime.datetime.now().strftime("%Y-%m-%d")

    steps_data = get_daily_steps(today, access_token)
    heart_rate_data = get_intraday_heart_rate(today, access_token)
    sleep_data = get_sleep_data(today, access_token)
    activity_summary = get_daily_activity_summary(today, access_token)

    data = get_data(url, access_token)
    pp.pprint(data['user'])

    ## Get the user's Fitbit data
    try:
        steps = int(steps_data["activities-steps"][0]["value"])
        heart_rate = heart_rate_data["activities-heart"][0]["value"]["restingHeartRate"]
        sleep_hours = sleep_data["summary"]["totalMinutesAsleep"] / 60
        activity_levels = activity_summary["summary"]["activeMinutes"]
    except KeyError:
        steps = None
        heart_rate = None
        sleep_hours = None
        activity_levels = None

    print(steps, heart_rate, sleep_hours, activity_levels)

    # Load mortality rates
    mortality_rates = load_mortality_rates(csv_file_path)

    ## Calculate the user's stroke risk score
    risk_score = calculate_stroke_risk(steps, heart_rate, sleep_hours, activity_levels)

    # Get the user's location (Replace with actual user input)
    user_location = "Michigan"

    # Find the mortality rate for the user's location
    mortality_rate = get_mortality_rate(user_location, mortality_rates)

    ## Compare the user's health data with the regional stroke mortality data
    comparison_result = compare_health_data(risk_score, mortality_rate)
if __name__ == "__main__":
    main()




