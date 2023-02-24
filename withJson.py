import json
from colorama import Fore


class withJson():
	""" Class for manage history chat

	Using json libriary

	"""

	def __init__(self, file):
		# path to file
		self.file = file 

	# Load all data from file
	def message_load(self):
		with open(self.file, "r") as file:
			opened_file = file.read()
			if opened_file == "":
				data = {}
			else:
				data = json.loads(opened_file)
			return data

	# Write messages to file
	def message_dump(self, messages):
		with open(self.file, "w") as file:
			json.dump(messages, file)

	# Get processed history
	def get_history_chat(self):
		text_message = ""
		messages = self.message_load()
		for i in messages:
			one_message = messages[i]
			for i in one_message:
				text_message += f"{Fore.YELLOW}{i}:\n {Fore.CYAN}{one_message.get(i)}"
		return text_message

	# Write processed history
	def write_messages_to_json(self, user, message):
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
