import threading
import socket
import json
import random
import time

used_ids = []
clients = []

print("Express to Nowhere SERVER")
print("designed for v0.5, should work onwards.")
print("USES PORT #29760 AND ONLY WORKS ON LOCAL NETWORK!")
print("so use Hamachi or smth, i dunno")
port = 29760

serverSocket = socket.socket()
try:
    serverSocket.bind(("", port))
    print("[LOG]", "Successfully installed port for socket")
except Exception as exc:
    print("[ERROR]", "Failed to install port for socket")
    print("[EXCEPTION]", exc)
    input()
    exit()

class Client:
    def __init__(self, socket, u_name, u_id):
        self.socket = socket
        self.socket.settimeout(5)
        self.name = u_name
        self.id = u_id

        self.player_trains = []
        self.server_trains = []

        self.thread = threading.Thread(target=self.thread)
        self.thread.start()

    def thread(self):
        running = True
        global clients

        while running:
            try:
                received = ""
                while True:
                    received += self.socket.recv(16384).decode("utf-8")
                    if not received:
                        running = False
                    if received[-1] == "=":
                        received = received[:-1]
                        break

                data = json.loads(received)

                self.player_trains = data
                
                reply = self.server_trains
                self.socket.send((json.dumps(reply) + "=").encode())
            except Exception as ex:
                print("[EXCEPTION]", ex)
                break

        print("[INFO] {} has disconnected".format(self.name, self.id))
        #chat.append({"user":"Server","text":"{} has disconnected".format(self.u_name)})
        self.socket.close()
        clients.remove(self)

working = True
MAX_CLIENTS = 1000

def general_thread():
    global working

    while working:
        trains = []
        for client in clients:
            trains.append(client.player_trains)

        for client in clients:
            client.server_trains = trains

        time.sleep(1/60)

gent = threading.Thread(target=general_thread)
gent.start()

while working:
    if len(clients) < MAX_CLIENTS:
        try:
            serverSocket.listen()
            connection, address = serverSocket.accept()
            print("zzz")
            try:
                nickname = connection.recv(16384).decode("utf-8")
                uid = random.randint(0,99999)
                while uid in used_ids: uid = random.randint(0,99999)
                reply = [str(uid)]
                reply = json.dumps(reply)
                connection.send((reply + "=").encode())
                print("[INFO]", "{} has connected".format(nickname))
                clients.append(Client(connection, nickname, uid))
                used_ids.append(uid)
            except Exception as exc:
                print("[ERROR]", "An unexpected error occured while client was connecting")
                print("[EXCEPTION]", exc)
                continue
        except: pass

gent.stop()