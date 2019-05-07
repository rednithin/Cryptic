# from NewsSentiment import NewsSentimentAnalysis
# from TwitterSentiment import TwitterSentimentAnalysis
from conf import get_config
import smtplib
from time import sleep
from app import db, User, Crypto


print("LOL")


for user in db.session.query(User).all():
    print(user.email)
    coins = list(map(lambda x: (x.name, x.short), user.cryptocurrencies))
    print(coins)

sleep(10)
# config = get_config()
# email = config["email"]
# password = config["password"]

# for user in db.session.query(User).all():
#     print(user.email)
#     coins = list(map(lambda x: (x.name, x.short), user.cryptocurrencies))
#     # coins = [("Bitcoin", "BTC"),("Litecoin", "LTC")]
#     sentiments = []
#     for coin in coins:
#         news_sentiment = NewsSentimentAnalysis(str(coin[0]))
#         print("News : ", news_sentiment)
#         if(news_sentiment is None):
#             news_sentiment = 0
#         twitter_sentiment = TwitterSentimentAnalysis(str(coin[0]))
#         print("Twitter : ", twitter_sentiment)
#         if(twitter_sentiment is None):
#             twitter_sentiment = 0
#         # reddit_sentiment = RedditSentimentAnalysis(coin[0])
#         final_sentiment = sum([news_sentiment, twitter_sentiment])/2
#         sentiments.append((coin, final_sentiment))

#     message = str(sentiments)
#     print(message)
#     mail = smtplib.SMTP('smtp.gmail.com', 587)
#     mail.ehlo()
#     mail.starttls()
#     mail.login(email, password)
#     mail.sendmail(email, user.email, str(message))
#     mail.close()
