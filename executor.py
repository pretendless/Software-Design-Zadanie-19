import models
import time
from datetime import datetime
from app import db

while 1:
	if datetime.now().strftime("%H:%M") == "23:59":
		for i in models.BotUsers.query.all():
			if i.subscribe == "Стандарт":
				i.tokens = 20
			else:
				i.tokens = 1
		db.session.commit()
		print("ok")
		time.sleep(72)
	time.sleep(5)
