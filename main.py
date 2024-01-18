import argparse
from configparser import ConfigParser
from urllib import error, parse, request
import sys
import json
import style

BASE_WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/"

# Weather Condition Codes
# https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
THUNDERSTORM = range(200, 300)
DRIZZLE = range(300, 400)
RAIN = range(500, 600)
SNOW = range(600, 700)
ATMOSPHERE = range(700, 800)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)


def display_weather_info(weather_data, imperial=False):
    city = weather_data["list"][0]["name"]
    weather_id = weather_data["list"][0]["weather"][0]["id"]
    weather_description = weather_data["list"][0]["weather"][0]["description"]
    temperature = weather_data["list"][0]["main"]["temp"]

    style.change_color(style.REVERSE)
    print(f"{city:^{style.PADDING}}", end="")
    style.change_color(style.RESET)

    weather_symbol, color = _select_weather_display_params(weather_id)

    style.change_color(color)
    print(f"\t{weather_symbol}", end=" ")
    print(f"\t{weather_description.capitalize():^{style.PADDING}}", end=" ")

    style.change_color(style.RESET)

    print(f"({temperature}°{'F' if imperial else 'C'})")


def _select_weather_display_params(weather_id):
    if weather_id in THUNDERSTORM:
        display_params = ("💥", style.RED)
    elif weather_id in DRIZZLE:
        display_params = ("💧", style.CYAN)
    elif weather_id in RAIN:
        display_params = ("💦", style.BLUE)
    elif weather_id in SNOW:
        display_params = ("⛄️", style.WHITE)
    elif weather_id in ATMOSPHERE:
        display_params = ("🌀", style.BLUE)
    elif weather_id in CLEAR:
        display_params = ("🔆", style.YELLOW)
    elif weather_id in CLOUDY:
        display_params = ("💨", style.WHITE)
    else:  # In case the API adds new weather codes
        display_params = ("🌈", style.RESET)
    return display_params


def read_user_cli_args():
    """Handles CLI user interactions"""
    parser = argparse.ArgumentParser(
        description="Gets weather and temperature info for a city."
    )
    parser.add_argument(
        "city", nargs="+", type=str, help="Enter the city name"
    )
    parser.add_argument(
        "-i",
        "--imperial",
        action='store_true',
        help="Display the temperature in imperial units",
    )
    return parser.parse_args()


def get_weather_data(query_url):
    """Makes an API request to a url and returns data as an object"""
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:
            sys.exit("Access denied. Check your API key.")
        if http_error.code == 404:
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")

    data = response.read()

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")


def _get_api_key():
    """Fetch the API key from config file
       Add your own API Key to make work"""
    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]


def build_weather_query(city_input, imperial=False):
    """Builds the URL for an API request to OpenWeather's API."""
    api_key = _get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (
        f"{BASE_WEATHER_API_URL}find?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}"
    )
    return url


if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city, user_args.imperial)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data, user_args.imperial)

