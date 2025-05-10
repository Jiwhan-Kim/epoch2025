import socket
import threading


def handle_receive_server(conn):
    while True:
        data = conn.recv(1024)      # read up to 1024 bytes
        if not data:                # b'' means client closed
            print("A disconnected")
            break
        print("A says:", data.decode().rstrip())


def handle_receive_client(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            print("B disconnected")
            break
        print("B says:", data.decode().rstrip())


if __name__ == '__main__':
    mode = input("Enter Mode ([s] for server, [<char> for client])")
    SERVER_IP = input("Enter IP Address of the server")
    SERVER_PORT = 65432

    if (mode == 'S' or mode == 's'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # (Optional) force your outgoing IP if you have multiple interfaces:
        # sock.bind(('192.168.10.10', 0))

        sock.connect((SERVER_IP, SERVER_PORT))
        print(f"A connected to B at {SERVER_IP}:{SERVER_PORT}")

        threading.Thread(target=handle_receive_client,
                         args=(sock,), daemon=True).start()
        handle_receive_server(sock)

        while True:
            msg = input("A> ")
            if not msg:
                break
            sock.sendall(msg.encode())

        sock.close()
    else:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # listen only on B’s 192.168.10.11
        srv.bind((SERVER_IP, SERVER_PORT))
        srv.listen(1)
        print(f"B listening on {SERVER_IP}:{SERVER_PORT}…")

        conn, addr = srv.accept()        # blocks until A connects
        print("Connected by", addr)
        threading.Thread(target=handle_receive_server,
                         args=(conn,), daemon=True).start()

        while True:
            reply = input("B> ")
            if not reply:
                break
            conn.sendall(reply.encode())

        conn.close()
