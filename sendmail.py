import smtplib
from conf import get_config
from TwitterSentimentNew import TwitterSentimentAnalysis
from NewsSentimentNew import NewsSentimentAnalysis
from RedditSentimentNew import RedditSentimentAnalysis
from time import sleep
from app import db, User, Crypto

config = get_config()
email = config["email"]
password = config["password"]

all_coins = set()
for user in db.session.query(User).all():
    print(user.email)
    coins = list(map(lambda x: (x.name, x.short), user.cryptocurrencies))
    all_coins = all_coins.union(set(coins))
print(all_coins)

coind = {}
for coin in all_coins:
    # news_sentiment = NewsSentimentAnalysis(str(coin[0]))
    # print("News : ", news_sentiment)
    twitter_sentiment = TwitterSentimentAnalysis(str(coin[0]))
    print("Twitter : ", twitter_sentiment)
    # reddit_sentiment = RedditSentimentAnalysis(str(coin[0]))
    # print("Reddit : ", reddit_sentiment)
    final_sentiment = twitter_sentiment
    coind[coin] = final_sentiment

    crypto = db.session.query(Crypto).filter_by(name=coin[0]).first()
    crypto.sentiment = coind[coin]
    db.session.commit()

for user in db.session.query(User).all():
    sentiments = []
    coins = list(map(lambda x: (x.name, x.short), user.cryptocurrencies))
    for coin in coins:
        final_sentiment = coind[coin]
        sentiments.append((coin, final_sentiment))

    # str(sentiments)
    message = "Market Sentiment for your favourite cryptocurrencies.\n"
    print(sentiments)
    for i in sentiments:
        message += i[0][0] + " : " + str(int(i[1])) + "% \n"
    print(message)

    if len(sentiments):
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        message = 'Subject: {}\n\n{}'.format('Sentiment Analysis', message)
        mail.login(email, password)
        mail.sendmail(email, user.email, str(message))
        mail.close()
