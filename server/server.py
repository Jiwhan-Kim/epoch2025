import socket
import threading

HOST = '192.168.219.104'   # server’s own address on the LAN
PORT = 65432


def handle_receive(conn):
    while True:
        data = conn.recv(1024)      # read up to 1024 bytes
        if not data:                # b'' means client closed
            print("A disconnected")
            break
        print("A says:", data.decode().rstrip())


srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.bind((HOST, PORT))           # listen only on B’s 192.168.10.11
srv.listen(1)
print(f"B listening on {HOST}:{PORT}…")

conn, addr = srv.accept()        # blocks until A connects
print("Connected by", addr)
threading.Thread(target=handle_receive, args=(conn,), daemon=True).start()

while True:
    reply = input("B> ")
    if not reply:
        break
    conn.sendall(reply.encode())

conn.close()
