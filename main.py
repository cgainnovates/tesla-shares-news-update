import os
import requests
import html
import smtplib
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import date, timedelta
from email.message import EmailMessage
load_dotenv()

sender = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")
STOCK_NAME = "TSLA"
STOCK_API = os.getenv("STOCK_API")
NEWS_API = os.getenv("NEWS_API")
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT =  "https://alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

stock_parameters = {
    "outputsize": "compact",
    "symbol": STOCK_NAME,
    "function": "TIME_SERIES_DAILY",
    "apikey": STOCK_API
}
news_parameters = {
    "qInTitle": COMPANY_NAME,
    "apiKey": NEWS_API,
    "language": "en",
    "sortBy": "relevancy"
}
stock_response = requests.get(
    url= STOCK_ENDPOINT,
    params= stock_parameters
)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]

today = date.today()
yesterday: date = today - timedelta(days=1)
day_before_yesterday = today - timedelta(days=2)
day_check_stocks = {
    "yesterday": float(stock_data[str(yesterday)]["4. close"]),
    "day_before_yesterday": float(stock_data[str(day_before_yesterday)]["4. close"])
}
percentage = round((day_check_stocks["yesterday"] - day_check_stocks["day_before_yesterday"])/day_check_stocks["yesterday"] * 100, 2)
abs_percentage = abs(round((day_check_stocks["yesterday"] - day_check_stocks["day_before_yesterday"])/day_check_stocks["yesterday"] * 100, 2))
if abs_percentage >= 5.0:
    note = (f"Percentage difference: {percentage}%\n"
            f"Yesterday's Stock Closing Price: ${day_check_stocks['yesterday']}\n"
            f"Day before yesterday Stock Closing Price: ${day_check_stocks['day_before_yesterday']}\n\n"
            )

    news_response = requests.get(
        url= NEWS_ENDPOINT,
        params=news_parameters
    )
    news_data = news_response.json()["articles"][:3]
    content = [
        {
            "author":html.unescape(x["author"]),
            "title":html.unescape(x["title"]),
            "description": html.unescape(x["description"]),
            "url": html.unescape(x["url"]),
            "content": BeautifulSoup(
            html.unescape(x["content"] or ""),
            "html.parser"
            ).get_text(separator="\n", strip=True)
        }
        for x in news_data
    ]
    msg = EmailMessage()
    msg['Subject'] = "Tesla Inc Shares News update"
    msg['from'] = sender
    msg['To'] = "chukwug996@gmail.com"
    body: list = [f"Author: {x['author']}\nTitle: {x['title']}\n"
                  f"Description: {x['description']}\nLink: {x['url']}\n\n"
                  f"{x['content']}" for x in content]
    body_text = '\n\n\n'.join(body)
    msg.set_content(
        f"{note}{body_text}"
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(msg)

