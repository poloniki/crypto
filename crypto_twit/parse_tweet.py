import os

import requests

RAPID_KEY = os.environ["RAPID_API_KEY"]

url = "https://twitter154.p.rapidapi.com/user/tweets"


def parse20tweets(username: str):

    querystring = {
        "username": username,
        "limit": "40",
        "include_replies": "false",
        "include_pinned": "false",
    }

    headers = {
        "x-rapidapi-key": RAPID_KEY,
        "x-rapidapi-host": "twitter154.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response


if __name__ == "__main__":
    print(parse20tweets("vitalikbuterin"))
