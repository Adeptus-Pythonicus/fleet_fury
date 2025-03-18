import requests
from typing import List

def get_weather() -> List | None:

    # Define the API endpoint and parameters
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        "latitude": 49.1664,
        "longitude": -123.94,
        "hourly": "windspeed_10m,winddirection_10m",
        "timezone": "auto"
    }

    # Make the API request
    response = requests.get(url, params=params)

    # Parse the JSON response
    if response.status_code == 200:
        data = response.json()
        current_windspeed = data['hourly']['windspeed_10m'][0]
        current_winddirection = data['hourly']['winddirection_10m'][0]
        print(f'Current wind speed: {current_windspeed} km/h')
        print(f'Current wind direction: {current_winddirection} km/h')
        return [current_windspeed, current_winddirection]
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None



if __name__ == '__main__':
    print(get_weather())

