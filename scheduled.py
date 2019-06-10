import smtplib
from conf import get_config
from TwitterSentimentNew import TwitterSentimentAnalysis
from NewsSentimentNew import NewsSentimentAnalysis
from RedditSentimentNew import RedditSentimentAnalysis
from subprocess import Popen

config = get_config()
email = config["email"]
password = config["password"]


def scheduled_mail():
    _ = Popen(['konsole', '-e', 'python sendmail.py'])
