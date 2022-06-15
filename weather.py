import requests
import json

def get_weather(x):
    if isinstance(x, int):
        arg = 'zip='+x
    else:
        arg = 'q='+x

    return json.loads(requests.get(f"https://api.openweathermap.org/data/2.5/weather?{arg}&appid={config.owm_auth}&units=imperial").text)