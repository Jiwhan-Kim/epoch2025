import socket
import threading

SERVER_IP = '192.168.219.104'  # server’s IP
SERVER_PORT = 65432


def handle_receive(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            print("B disconnected")
            break
        print("B says:", data.decode().rstrip())


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# (Optional) force your outgoing IP if you have multiple interfaces:
# sock.bind(('192.168.10.10', 0))

sock.connect((SERVER_IP, SERVER_PORT))
print(f"A connected to B at {SERVER_IP}:{SERVER_PORT}")

threading.Thread(target=handle_receive, args=(sock,), daemon=True).start()

while True:
    msg = input("A> ")
    if not msg:
        break
    sock.sendall(msg.encode())

sock.close()
