import requests
import streamlit as st
from openai import OpenAI
from textblob import TextBlob
import pandas as pd
import numpy as np
from collections import Counter

# Secrets for API keys
RAPID_KEY = st.secrets["RAPID_API_KEY"]
OPENAI_KEY = st.secrets["OPENAI_API_KEY"]

# Twitter API endpoint
url = "https://twitter154.p.rapidapi.com/user/tweets"


# Function to fetch tweets from Twitter API
@st.cache_data
def fetch_tweets(username: str):
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
    return response.json()


# OpenAI client setup
client = OpenAI(api_key=OPENAI_KEY)

st.title("Crypto Tweets Summarization and Analysis")


# Function to summarize tweets
def summarize_tweets(tweets):
    tweets_text = "\n\n".join(tweet["text"] for tweet in tweets["results"])
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """You are a Crypto Analyst who tries to make profitable buys and sells.
                You make brief analyses of tweets to highlight the most significant parts if there is anything relevant.
                Try to make short bullet points. Do not just restate the content of the tweet - give me conclusions from its content.
                """,
            },
            {"role": "user", "content": tweets_text},
        ],
        model="gpt-4",
    )

    message = response.choices[0].message.content
    return message


# Function to perform sentiment analysis
def sentiment_analysis(tweets):
    sentiments = []
    for tweet in tweets["results"]:
        analysis = TextBlob(tweet["text"])
        sentiment = analysis.sentiment.polarity
        if sentiment > 0.1:
            sentiment_label = "Happy"
        elif sentiment < -0.1:
            sentiment_label = "Sad"
        else:
            sentiment_label = "Neutral"
        sentiments.append(sentiment_label)
    return sentiments


# Input for multiple Twitter usernames
usernames = st.text_area(
    "Insert Twitter usernames (comma-separated)",
    value="brian_armstrong,vitalikbuterin,APompliano,RaoulGMI",
)

# Button to trigger analysis
button = st.button("Analyze last 40 Tweets of each account")

# If button is pressed
if button:
    all_tweets = []
    user_sentiments = {}
    for username in usernames.split(","):
        username = username.strip()
        tweets = fetch_tweets(username)
        all_tweets.extend(tweets["results"])
        sentiments = sentiment_analysis(tweets)
        user_sentiments[username] = sentiments

    if all_tweets:
        # Summarize tweets
        summary = summarize_tweets({"results": all_tweets})

        # Styling for bullet points
        styled_summary = (
            """
        <style>
        ul {
            list-style-type: disc;
            margin-left: 20px;
        }
        li {
            font-size: 16px;
            line-height: 1.6;
            color: #333;
            margin-bottom: 10px;
        }
        </style>
        <ul>
        """
            + "".join(
                f"<li>{line.strip()}</li>"
                for line in summary.split("\n")
                if line.strip()
            )
            + "</ul>"
        )

        st.markdown(styled_summary, unsafe_allow_html=True)

        # Overall sentiment for each account
        sentiment_counts = {
            username: Counter(sentiments)
            for username, sentiments in user_sentiments.items()
        }
        sentiment_df = pd.DataFrame(sentiment_counts).fillna(0).astype(int)
        st.subheader("Overall Sentiment for Each Account")
        st.bar_chart(sentiment_df)

        # Display tweet texts with engagement in a nice dataframe
        tweet_data = {
            "Tweet Text": [tweet["text"] for tweet in all_tweets],
            "Likes": [tweet["favorite_count"] for tweet in all_tweets],
            "Retweets": [tweet["retweet_count"] for tweet in all_tweets],
            "Replies": [tweet["reply_count"] for tweet in all_tweets],
            "Quotes": [tweet["quote_count"] for tweet in all_tweets],
        }
        tweet_df = pd.DataFrame(tweet_data)
        st.dataframe(
            tweet_df,
            column_config={
                "Tweet Text": "Tweet Text",
                "Likes": st.column_config.NumberColumn("Likes", format="%d 👍"),
                "Retweets": st.column_config.NumberColumn("Retweets", format="%d 🔁"),
                "Replies": st.column_config.NumberColumn("Replies", format="%d 💬"),
                "Quotes": st.column_config.NumberColumn("Quotes", format="%d 🗨️"),
            },
            hide_index=True,
        )
    else:
        st.text("No tweets found for the provided usernames.")
