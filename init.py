from app import db, User, Crypto

db.create_all()

coins = [("Bitcoin", "BTC"),
         ("Litecoin", "LTC"),
         ("Ethereum", "ETH"),
         ("Ripple", "XRP"),
         ("Monero", "XMR"),
         ("Binance Coin", "BNB")]

for name, short in coins:
    c = Crypto(name=name, short=short)
    try:
        db.session.add(c)
        db.session.commit()
    except:
        pass
