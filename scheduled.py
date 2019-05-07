import smtplib
from conf import get_config
from subprocess import Popen

config = get_config()
email = config["email"]
password = config["password"]


# def scheduled_mail():
#     from app import db, User, Crypto
#     print('HAHAHAH')
#     mail = smtplib.SMTP('smtp.gmail.com', 587)
#     mail.ehlo()
#     mail.starttls()
#     mail.login(email, password)
#     for user in db.session.query(User).all():
#         print(user.email)
#         coins = list(map(lambda x: (x.name, x.short), user.cryptocurrencies))
#         '''
#         coins is of the form
#         [
#             ("Bitcoin", "BTC"),
#             ("Litecoin", "LTC")
#         ]
#         '''
#         '''


#         PUSHKALA MODIFY THIS PART


#         '''
#         message = str(coins)
#         # mail.sendmail(email, [user.email], str(message))
#     mail.close()

def scheduled_mail():
    script = f'python sendmail.py'
    print(script)
    _ = Popen(['konsole', '-e', script])
