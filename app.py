# from scheduled import scheduled_mail
from flask import Flask, request, jsonify
import redis
from rq import Queue
from rq.registry import FailedJobRegistry, FinishedJobRegistry, StartedJobRegistry
from binance.client import Client
from flask_cors import CORS, cross_origin
import random
import pandas as pd
import numpy as np
from os import listdir
import toml
from copy import deepcopy
from random import choice
from pprint import pprint
from subprocess import Popen
from flask_sqlalchemy import SQLAlchemy
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
from background import binance, hyper_param_optimize
# from flask_marshmallow import Marshmallow

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'True'

db = SQLAlchemy(app)
# ma = Marshmallow(app)
r = redis.Redis()
scheduler = Scheduler('mail', connection=r, interval=300)
q = Queue(connection=r)


months_map = {
    "01": "Jan",
    "02": "Feb",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}

association = db.Table('association', db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('crypto_id', db.Integer, db.ForeignKey('crypto.id')))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    cryptocurrencies = db.relationship(
        'Crypto', secondary=association, backref=db.backref('users'))


class Crypto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    short = db.Column(db.String(5), unique=True)
    sentiment = db.Column(db.Float, default=-1.0)


def get_hash(mystring):
    import hashlib
    hash_object = hashlib.md5(mystring.encode())
    return hash_object.hexdigest()


@app.route("/tasks")
def tasks():
    response = {
        'pending': q.get_job_ids()[::-1],
        'finished': FinishedJobRegistry('default', connection=r, queue=q).get_job_ids()[::-1],
        'failed': FailedJobRegistry('default', connection=r, queue=q).get_job_ids()[::-1],
        'running': StartedJobRegistry('default', connection=r, queue=q).get_job_ids()[::-1]
    }
    return jsonify(response)


# @app.route("/login", methods=['POST'])
# def login():
#     payload = request.get_json()
#     if payload["email"] == "reddy.nithinpg@gmail.com" and payload["password"] == "12345678":
#         return jsonify({"status": True})
#     return jsonify({"status": False})


# @app.route("/setup", methods=['POST'])
# def setup():
#     payload = request.get_json()
#     if payload["email"] == "reddy.nithinpg@gmail.com" and payload["password"] == "12345678":
#         return jsonify({"status": True})
#     return jsonify({"status": False})


@app.route("/dataset", methods=['POST'])
def dataset():
    payload = request.get_json()
    d1 = payload["daterange"][0][:10].split("-")
    d2 = payload["daterange"][1][:10].split("-")
    payload["start_date"] = f"{d1[2]} {months_map[d1[1]]}, {d1[0]}"
    payload["end_date"] = f"{d2[2]} {months_map[d2[1]]}, {d2[0]}"

    if payload["exchange"] == "Binance":
        columns = [
            'Open Time',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume',
            'Close Time',
            'Quote Asset Volume',
            'Number Of Trades',
            'Taker Buy Base Asset Volume',
            'Taker Buy Quote Asset Volume',
            'Ignore'
        ],
        interval = payload["interval"]
        if interval == "1m":
            payload["interval"] = Client.KLINE_INTERVAL_1MINUTE
        elif interval == "3m":
            payload["interval"] = Client.KLINE_INTERVAL_3MINUTE
        elif interval == "5m":
            payload["interval"] = Client.KLINE_INTERVAL_5MINUTE
        elif interval == "15m":
            payload["interval"] = Client.KLINE_INTERVAL_15MINUTE
        elif interval == "30m":
            payload["interval"] = Client.KLINE_INTERVAL_30MINUTE
        elif interval == "1h":
            payload["interval"] = Client.KLINE_INTERVAL_1HOUR
        elif interval == "2h":
            payload["interval"] = Client.KLINE_INTERVAL_2HOUR
        elif interval == "4h":
            payload["interval"] = Client.KLINE_INTERVAL_4HOUR
        elif interval == "6h":
            payload["interval"] = Client.KLINE_INTERVAL_6HOUR
        elif interval == "8h":
            payload["interval"] = Client.KLINE_INTERVAL_8HOUR
        else:
            return jsonify({"error": True}), 500
        job = q.enqueue(binance, columns=columns, **payload)
        return jsonify({"queued": True, "id": job.id})
    return jsonify({"error": True}), 500


@app.route("/filenames")
def filenames():
    filenames = list(filter(lambda x: x.endswith(".csv"), listdir('data')))
    return jsonify(filenames)


@app.route("/coins", methods=['POST'])
def coins():
    payload = request.get_json()
    user_id = payload["user"]
    user = db.session.query(User).get(user_id)
    user_coins = []
    for c in user.cryptocurrencies:
        user_coins.append(c.name)

    coins = Crypto.query.all()
    coins = list(map(lambda x: x.name, coins))

    return jsonify({"coins": coins, "userCoins": user_coins})


@app.route("/add_coins", methods=['POST'])
def add_coins():
    payload = request.get_json()
    user_id = payload["user"]
    new_coins = payload["coins"]

    user = db.session.query(User).get(user_id)
    if user:
        user.cryptocurrencies = []
        for name in new_coins:
            coin = db.session.query(Crypto).filter_by(name=name).first()
            if coin:
                user.cryptocurrencies.append(coin)
    db.session.commit()
    return jsonify({"userCoins": new_coins})


@app.route("/strategies")
def strategies():
    # def add_hyper(x):
    #     y = {"name": x[:-3]}
    #     with open(f'strategies/{x[:-3]}.toml') as f:
    #         y["config"] = f.read()
    #     with open(f'strategies/{x[:-3]}_hyper.toml') as f:
    #         y["hyper"] = f.read()
    #     return y

    def get_configs(name):
        # name = x["name"]
        filenames = list(filter(lambda x: x.endswith(".toml"),
                                listdir(f'strategies/{name}')))
        d = {}
        for file in filenames:
            with open(f'strategies/{name}/{file}') as f:
                d[file[:-5]] = f.read()
        return d

    def get_hyper(name):
        with open(f'strategies/{name}_hyper.toml') as f:
            return f.read()

    filenames = list(
        filter(lambda x: x.endswith(".py"), listdir('strategies')))
    strategies = list(map(lambda x: x[:-3], filenames))

    d = {}
    h = {}
    for strat in strategies:
        d[strat] = get_configs(strat)
    for strat in strategies:
        h[strat] = get_hyper(strat)
    return jsonify([strategies, d, h])


@app.route("/backtest", methods=['POST'])
def backtest():
    features = [
        # 'Open Time',
        'Open',
        'High',
        'Low',
        'Close',
        'Volume',
        # 'Close Time',
        # 'Quote Asset Volume',
        # 'Number Of Trades',
        # 'Taker Buy Base Asset Volume',
        # 'Taker Buy Quote Asset Volume',
        # 'Ignore'
    ]
    payload = request.get_json()
    module = __import__(
        f'strategies.{payload["strategy"]}', fromlist=['MyStrat'])
    Strat = getattr(module, 'MyStrat')
    df = pd.read_csv(f'data/{payload["filename"]}')
    df = df[features]
    strat = Strat(df, payload["warmup"], user_config=payload['config'])
    _, response = strat.backtest()
    return jsonify(response)


@app.route("/hyperopt", methods=['POST'])
def hyperopt():
    payload = request.get_json()
    # hyper_param_optimize(payload)
    job = q.enqueue(hyper_param_optimize, payload)
    return jsonify({"queued": True, "id": job.id})


@app.route("/papertrading", methods=['POST'])
def papertrading():
    payload = request.get_json()
    script = f'python live.py -e {payload["exchange"]} -i {payload["interval"]} -p {payload["pair"]} -s {payload["strategy"]} -w {payload["warmup"]}'
    print(script)
    with open('temp.toml', 'w') as f:
        f.write(payload['config'])
    _ = Popen(['konsole', '-e', script])
    return jsonify({})


@app.route("/login", methods=['POST'])
def login():
    payload = request.get_json()
    user = db.session.query(User).filter_by(email=payload["email"]).first()
    if user:
        if user.password == get_hash(payload["password"]):
            return jsonify({"user": user.id})
        else:
            return jsonify({}), 401
    else:
        return jsonify({}), 404


@app.route("/setup", methods=['POST'])
def setup():
    payload = request.get_json()
    print(payload)
    user = User(name=payload["name"], email=payload["email"],
                password=get_hash(payload["password"]))
    db.session.add(user)
    db.session.commit()
    return jsonify({"user": user.id})


for job in scheduler.get_jobs():
    scheduler.cancel(job)


# scheduler.schedule(
#     scheduled_time=datetime.utcnow(),
#     func=scheduled_mail,
#     # args=[],
#     # kwargs={},
#     interval=300,  # Seconds
#     repeat=None,
#     result_ttl=1
# )


@app.after_request
def after_request(response):
    l = list(scheduler.get_jobs())
    print('Current Jobs :', l)
    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)
