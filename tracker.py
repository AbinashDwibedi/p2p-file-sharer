import socket 
import json
import struct

PORT = 65000
HOST = "0.0.0.0"

resources = {}

with socket.socket(socket.AF_INET,socket.SOCK_STREAM)as s:
    s.bind((HOST,PORT))
    s.listen()

    print("Tracker server is running successfully.")
    while True:
        conn, addr = s.accept()
        try:
            received = conn.recv(4)
            header_len = struct.unpack("!I",received)[0]
            received = conn.recv(header_len).decode("utf-8")
            header = json.loads(received)

            action = header.get("action")
            if action == "ANNOUNCE":
                for file_info in header["files"]:
                    fname = file_info["name"]
                    if fname not in resources:
                        resources[fname] = []
                    peer_info = (addr[0],header["port"])
                    if peer_info not in resources[fname]:
                        resources[fname].append(peer_info)
                print("files resistered")
                print(resources)
            if action == "LOOKUP":
                fname = header["name"]
                peers = resources.get(fname,[])
                peers_bytes = json.dumps(peers).encode("utf-8")
                peers_len = struct.pack("!I",len(peers_bytes))
                conn.sendall(peers_len)
                conn.sendall(peers_bytes)


        except Exception as e:
            print("Something went wrong",e)
        finally :
            conn.close()