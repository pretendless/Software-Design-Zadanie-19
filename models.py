from app import db


def auto_repr(self):
	""" Автоматическое REPR форматирование для обьектов """
	base_repr = "<{}(".format(self.__class__.__name__)
	for name in self.__dict__:
		if name[0] == "_":
			continue
		value = self.__dict__[name]
		base_repr += "{}='{}',".format(name,value)
	base_repr = base_repr[:-1]
	base_repr += ")>"
	return base_repr



class BotUsers(db.Model):
	""" Модель юзеров бота """
	__tablename__ = "bot_user"
	id = db.Column(db.Integer(), primary_key=True)  
	user_id = db.Column(db.String())
	user_name = db.Column(db.String())
	user_firstname = db.Column(db.String())
	subscribe = db.Column(db.String(), default="Нет подписки")
	tokens = db.Column(db.Integer(), default=1)


	def __repr__(self):
		return auto_repr(self)


class BanWords(db.Model):
	""" Модель юзеров бота """
	__tablename__ = "ban_words"
	id = db.Column(db.Integer(), primary_key=True)  
	word = db.Column(db.String())
	


	def __repr__(self):
		return auto_repr(self)



db.create_all()
db.session.commit()







