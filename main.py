import socket
from select import select
from app import connection_users, to_read, to_write, tasks, with_json
from colorama import Fore, Back


def server():
	"""Create server socket and connection reception

	Using libriary socket

	"""
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Allow the server socket to reuse connections on the same address.
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(("localhost", 5000))
	server_socket.listen()

	while True:
		# Return the sign of the blocking function and the socket
		yield ("read", server_socket)
		client_socket, addr = server_socket.accept()
		# Create a new task for the event handler by adding a generator object to the task list
		tasks.append(registration_user_socket(client_socket))


def registration_user_socket(client_socket):
	""" Connection registration by entered username

	Using libriary socket

	"""

	# Return the sign of the blocking function and the socket
	yield ("write", client_socket)
	client_socket.send("Enter your name: ".encode())

	# Return the sign of the blocking function and the socket
	yield ("read", client_socket)
	name_user = client_socket.recv(1024).decode()[:-1]

	# Add a new user to the list of connected users
	connection_users[client_socket] = name_user
	print(f"{Fore.GREEN}Connection from user:", name_user)
	tasks.append(send_history_to_user(client_socket))


def disconnect_user_socket(client_socket):
	disconected_user = connection_users.pop(client_socket)
	print(f"{Fore.RED}User {disconected_user} was disconnected!")
	to_read.pop(client_socket)
	

def send_history_to_user(client_socket):
	# Return the sign of the blocking function and the socket
	yield ("write", client_socket)
	response = f"{with_json.get_history_chat()}\n{Fore.CYAN}You:\n  {Fore.GREEN}".encode()
	client_socket.send(response)

	# Create a new task for the event handler by adding a generator object to the task list
	tasks.append(client(client_socket))


def client(client_socket):
	"""A generator that receives a message from a connected user
	   and sends it to all connected sockets
	
	Using class withJson. The class object is created in the app.py file
	Using libriary socket

	"""
	while True:
		# Return the sign of the blocking function and the socket
		yield ("read", client_socket)
		request = client_socket.recv(4096).decode()

		# Adds the message to a Json file with the message history.
		# If there are more than 10 messages each item is shifted by one
		with_json.write_messages_to_json(connection_users[client_socket], request)


		# Mailing to all connected users
		if request:
			for sock in connection_users:
				if sock is client_socket:
					continue
				else:
					# Return the sign of the blocking function and the socket
					yield ("write", client_socket)
					sock.send(f"{Fore.YELLOW}{connection_users[client_socket]}:\n  {Fore.GREEN}{request}{Fore.CYAN}You:\n  {Fore.GREEN}".encode())
		else:
			disconnect_user_socket(client_socket)
			client_socket.close()


def event_loop():
	""" Function controlling generators

	Using libriary select
	"""
	while any([tasks, to_read, to_write]):
		
		while not tasks:
			# Returns lists with objects that have a file descriptor,
			# Available for reading or writing
			ready_to_read, ready_to_write, _ = select(to_read, to_write, [])

			# Go through the list of readable sockets and add the function object to the tasks list
			for i in ready_to_read:
				tasks.append(to_read.pop(i))

			# Go through the list of writable sockets and add the function object to the list of tasks
			for i in ready_to_write:
				tasks.append(to_write.pop(i))
		try:
			# Take the first item in the list, removing it and advancing the generator
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
