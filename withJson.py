import json


class withJson():
	""" Индивидуальный клас для работы с Json

	Используется библиотека Json

	"""

	def __init__(self, file):
		""" Инициализируем клас

		"""
		# Путь к файлу
		self.file = file 

	def message_load(self):
		""" Загружаем все данные из файла

		"""
		with open(self.file, "r") as file:
			data = json.load(file)
			return data

	def message_dump(self, messages):
		""" Загружаем данные в файл

		"""
		with open(self.file, "w") as file:
			json.dump(messages, file)

	def get_history_chat(self):
		""" Получаем обработаную историю сообщений

		Используется метод message_load

		"""
		text_message = ""
		messages = self.message_load()
		for i in messages:
			one_message = messages[i]
			for i in one_message:
				text_message += f"{i}:\n {one_message.get(i)}\n"
		return text_message

	def write_messages_to_json(self, user, message):
		""" Загружаем обработаную историю сообщений

		Используются методы message_load и message_dump

		"""
		data_json = {}
		messages = self.message_load()
		if len(messages) == 10:
			for i in messages:
				key = int(i) - 1
				data_json[str(key)] = messages[i]
			del data_json["0"]
			data_json[len(data_json)+1] = {user: message}
			self.message_dump(data_json)
		else:
			messages[len(messages)+1] = {user: message}
			self.message_dump(messages)


