import threading
import socket
import struct
import json
import os

class ServerNode:
    def __init__(self, assets_path, host="127.0.0.1", port=64500):
        self.assets_path = assets_path
        self.host = host
        self.port = port
        self.tracker_ip = "127.0.0.1"
        self.tracker_port = 65000

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            self._announce_to_tracker()
            while True:
                conn, addr = s.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                thread.start()

    def handle_client(self, conn, addr):
        try:
            received = conn.recv(4)
            if not received:return
            header_len = struct.unpack("!I", received)[0]
            header_data = conn.recv(header_len).decode("utf-8")
            header = json.loads(header_data)
            
            if header["action"] == "HELLO":
                self._send_header(conn, {"action": "READY"})
                
                received = conn.recv(4)
                if not received:return
                header_len = struct.unpack("!I", received)[0]
                header_data = conn.recv(header_len).decode("utf-8")
                header = json.loads(header_data)
                
                if header["action"] == "FILE":
                    # file_name = header["name"]
                    # file_data = self.get_file_details(file_name)
                    # if not file_data:
                    #     return
                    
                    # self._send_header(conn, file_data)
                    
                    while True:
                        received = conn.recv(4)
                        if not received:
                            break
                        header_len = struct.unpack("!I", received)[0]
                        header_data = conn.recv(header_len).decode("utf-8")
                        header = json.loads(header_data)
                        
                        file_name = header["name"]
                        piece_idx = header["piece_idx"]
                        piece_size = header["piece_size"]
                        
                        file_path = os.path.join(self.assets_path, file_name)
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                f.seek(piece_idx * piece_size)
                                conn.sendall(f.read(piece_size))
                        else:
                            return 

        except Exception:
            print("something went wrong")
        finally:
            conn.close()

    def _send_header(self, conn, header):
        header_bytes = json.dumps(header).encode("utf-8")
        header_len = struct.pack("!I", len(header_bytes))
        conn.sendall(header_len)
        conn.sendall(header_bytes)

    def _announce_to_tracker(self):
        files = self.get_file_list()
        header = {
            "action": "ANNOUNCE",
            "files": files,
            "port": self.port
        }
        self._send_header_to_tracker(header)

    def _send_header_to_tracker(self, header):
        header_bytes = json.dumps(header).encode("utf-8")
        header_len = struct.pack("!I", len(header_bytes))
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.tracker_ip, self.tracker_port))
                s.sendall(header_len)
                s.sendall(header_bytes)
        except:
            pass

    def get_file_list(self):
        files = []
        if os.path.exists(self.assets_path):
            for filename in os.listdir(self.assets_path):
                path = os.path.join(self.assets_path, filename)
                if os.path.isfile(path):
                    files.append({
                        "name": filename,
                        "size": os.path.getsize(path)
                    })
        return files

    def get_file_details(self, file_name):
        path = os.path.join(self.assets_path, file_name)
        if os.path.exists(path):
            file_size = os.path.getsize(path)
            return {
                "size": file_size,
                "name": file_name,
            }
        else:
            return {}

def server_node(assets_path):
    server = ServerNode(assets_path)
    server.start()
