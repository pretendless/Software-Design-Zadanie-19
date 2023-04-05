import telebot
import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from tb_forms import TelebotForms, ffsm
from flask_redis import FlaskRedis



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['REDIS_URL'] = config.REDIS_URL


redis_client = FlaskRedis(app)
bot = telebot.TeleBot(config.TOKEN, skip_pending=True)
fsm = ffsm.RedisFSM(redis_client)
db = SQLAlchemy(app)







