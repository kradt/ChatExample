import socket
from select import select
from app import connection_users, to_read, to_write, tasks, with_json
from colorama import Fore, Back


def server():
	"""Создание серверного сокета и прием подключений

	Используется встроенный клас socket

	"""
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Позволяем серверному сокету переиспользовать подключния по тому же самому адресу.
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(("localhost", 5000))
	server_socket.listen()

	while True:
		# Возвращаем признак блокирующей функции и сокет
		yield ("read", server_socket)
		client_socket, addr = server_socket.accept()
		# Создаем новою задачу для обработчика событий добавляя объект генератора в список task
		tasks.append(registration_user_socket(client_socket))


def registration_user_socket(client_socket):
	""" Регистация подключения по введеному имени пользователя

	Используется встроенный клас socket

	"""

	# Возвращаем признак блокирующей функции и сокет
	yield ("write", client_socket)
	client_socket.send("Enter your name: ".encode())

	# Возвращаем признак блокирующей функции и сокет
	yield ("read", client_socket)
	name_user = client_socket.recv(1024).decode()[:-1]

	# Добавляем в список подключенных пользователей нового
	connection_users[client_socket] = name_user
	print(f"{Fore.GREEN}Connection from user:", name_user)
	tasks.append(send_history_to_user(client_socket))


def disconnect_user_socket(client_socket):
	disconected_user = connection_users.pop(client_socket)
	print(f"{Fore.RED}User {disconected_user} was disconnected!")
	to_read.pop(client_socket)
	


def send_history_to_user(client_socket):
	# Возвращаем признак блокирующей функции и сокет
	yield ("write", client_socket)
	response = f"{with_json.get_history_chat()}\n{Fore.CYAN}You:\n  {Fore.GREEN}".encode()
	client_socket.send(response)

	# Создаем новою задачу для обработчика событий добавляя объект генератора в список task
	tasks.append(client(client_socket))


def client(client_socket):
	"""Генератор получающий сообщения от подключенного пользователя
	   и рассылающий его по всем подключенным сокетам
	
	Генератор использует клас withJson. Oбъект класса создан в файле app.py
	Используется встроенный клас socket

	"""
	while True:
		# Возвращаем признак блокирующей функции и сокет
		yield ("read", client_socket)
		request = client_socket.recv(4096).decode()

		# Добавления сообщения в Json файл с историей сообщений.
		# Если сообщений больше 10 каждый элемент смещается на один
		with_json.write_messages_to_json(connection_users[client_socket], request)


		# Рассылка по всем подключенным пользователям
		if request:
			for sock in connection_users:
				if sock is client_socket:
					continue
				else:
					# Возвращаем признак блокирующей функции и сокет
					yield ("write", client_socket)
					sock.send(f"{Fore.YELLOW}{connection_users[client_socket]}:\n  {Fore.GREEN}{request}{Fore.CYAN}You:\n  {Fore.GREEN}".encode())
		else:
			disconnect_user_socket(client_socket)
			client_socket.close()


def event_loop():
	""" Функция управляющая генераторами

	Функция использует метод select
	"""
	while any([tasks, to_read, to_write]):
		
		while not tasks:
			# Возвращает списки с объектами имеющие файловый дескриптор,
			# Доступные для чтения либо для записи
			ready_to_read, ready_to_write, _ = select(to_read, to_write, [])

			# Проходим по списку доступных для чтения сокетов и добавляем объект фунции в список tasks
			for i in ready_to_read:
				tasks.append(to_read.pop(i))

			# Проходим по списку доступных для записи сокетов и добавляем объект функции в список tasks
			for i in ready_to_write:
				tasks.append(to_write.pop(i))
		try:
			# Берем первый елемент в списке удаляя его и продвигаем генератор
			task = tasks.pop(0)
			reason, sock = next(task)

			if reason == "read":
				to_read[sock] = task
				
			if reason == "write":
				to_write[sock] = task
		except:
			pass


if __name__ == "__main__":
	# Create a new task for the evenv loop by adding an object generator to the task list
	tasks.append(server())
	event_loop()
