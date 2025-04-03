import requests
import logging
import random
from time import sleep
from math import cos, sin, radians
from typing import List
from requests.exceptions import SSLError


logging.basicConfig(level=logging.DEBUG)  # or INFO, WARNING, ERROR, CRITICAL

class WindModifier():

    def __init__(self):
        # [wind speed, direction (in polar coordinate)]
        self.wind_values = []

    def cyclic_modulus(self, x, min_val=0, max_val=9):
        '''
        So if the wind shifts the impact point off the playable grid,
        it rolls over back from the other side of the grid.
        '''
        range_size = max_val - min_val + 1
        return ((x - min_val) % range_size) + min_val

    def determine_shift(self, coords: List):
        logging.info(f'Unshifted coords: {coords}')

        try:
            speed = self.wind_values[0]
            x = self.wind_values[1]
        except Exception as e:
            logging.error("No wind data assigned to determine impact shifts.")
            return None

        # Determine intensity multiplier
        if speed > 15:
            multiplier = 2
        elif speed > 5:
            multiplier = 1
        else:
            multiplier = 0

        dx, dy = 0, 0

        match x:
            case x if 0 <= x < 22.5:
                logging.info(f'Wind blows East')
                dx, dy = 1, 0
            case x if 22.5 <= x < 67.5:
                logging.info(f'Wind blows North East')
                dx, dy = 1, -1
            case x if 67.5 <= x < 112.5:
                logging.info(f'Wind blows North')
                dx, dy = 0, -1
            case x if 112.5 <= x < 157.5:
                logging.info(f'Wind blows North West')
                dx, dy = -1, -1
            case x if 157.5 <= x < 202.5:
                logging.info(f'Wind blows West')
                dx, dy = -1, 0
            case x if 202.5 <= x < 247.5:
                logging.info(f'Wind blows South West')
                dx, dy = -1, 1
            case x if 247.5 <= x < 292.5:
                logging.info(f'Wind blows South')
                dx, dy = 0, 1
            case x if 292.5 <= x < 337.5:
                logging.info(f'Wind blows South East')
                dx, dy = 1, 1
            case x if 337.5 <= x < 360:
                logging.info(f'Wind blows East')
                dx, dy = 1, 0
            case _:
                raise ValueError("Angle x must be in [0, 360) degrees")

        # Apply wind intensity
        coords[0] += dx * multiplier
        coords[1] += dy * multiplier

        coords[0] = self.cyclic_modulus(coords[0])
        coords[1] = self.cyclic_modulus(coords[1])

        logging.info(f'Shifted coords: {coords}')
        return coords

    def wind_direction_polar(self, wind_dir: int):
        # Convert the Azimuth to Polar Coordinate degrees
        polar_degree = (450 - wind_dir) % 360

        '''
        But remember, we also need to flip the polar
        direction since the API gives us the azimuth direction
        of the SOURCE of the wind.
        '''
        flipped_direction = (polar_degree + 180) % 360
        return flipped_direction

    def get_weather_data(self) -> None:

        # Define the API endpoint and parameters
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            "latitude": 49.1664,
            "longitude": -123.94,
            "hourly": "windspeed_10m,winddirection_10m",
            "timezone": "auto"
        }

        current_windspeed = None
        current_winddirection = None
        try:
            # Make the API request
            response = requests.get(url, params=params)

            # Parse the JSON response
            if response.status_code == 200:
                data = response.json()
                current_windspeed = data['hourly']['windspeed_10m'][0]
                current_winddirection = data['hourly']['winddirection_10m'][0]
                logging.info(f'Current wind speed: {current_windspeed} km/h')
                logging.info(f'Current wind direction: {current_winddirection} azimuth')
            else:
                logging.info(f"Error: Unable to fetch data. Status code: {response.status_code}")
        except SSLError as e:
            print("No response from third-party service")
        except Exception as e:
            print(type(e))
        finally:
            if not current_winddirection and not current_windspeed:
                '''
                An exception was raised and we were not given data.
                '''
                logging.info(f'Network error. Wind disabled for now.')
                self.wind_values = [0, 0]

                #logging.info(f'Network error. Random wind values provided.')
                #self.wind_values = [random.randrange(0, 40), random.randrange(0,360)]

            else:
                self.wind_values = [current_windspeed, self.wind_direction_polar(current_winddirection)]



if __name__ == '__main__':
    # Usage example:
    x = WindModifier()
    x.get_weather_data()
    print(x.wind_values)

    x.determine_shift([0,0])
    x.determine_shift([9,9])
    x.determine_shift([0,9])
    x.determine_shift([9,0])
