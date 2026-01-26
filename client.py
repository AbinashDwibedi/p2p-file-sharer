import socket
import os
import json
import struct
import math
import threading
import hashlib

class ClientNode:
    def __init__(self, piece_size):
        self.piece_size = piece_size
        self.tracker_ip = "127.0.0.1"
        self.tracker_port = 65000
        self.lock = threading.Lock()
        self.bitfield = []
    
    def start(self):
        while True:
            file_name = input("Enter the filename you want to download (or 'q' to quit): ")
            if file_name.lower() == 'q':
                break
            self._receive_file_swarm(file_name)
    def verify_client_integrity(self,filename,expected_hash):
        sha256_hash = hashlib.sha256()
        try:
            with open(filename,"rb")as f:
                for byte_block in iter(lambda:f.read(4096),b""):
                    sha256_hash.update(byte_block)
            calculated_hash = sha256_hash.hexdigest()
            if calculated_hash == expected_hash:
                print(f"Integrity Verified! {filename} is perfect.")
                return True
            else:
                print(f"CORRUPTION DETECTED! Hash mismatch.")
                print(f"Expected: {expected_hash}")
                print(f"Got:      {calculated_hash}")
                return False
        except Exception as e:
            print("Something went wrong!",e)
            return False
    def lookup_from_tracker(self, filename):
        header = {
            "action": "LOOKUP",
            "name": filename
        }
        header_bytes = json.dumps(header).encode("utf-8")
        header_len = struct.pack("!I", len(header_bytes))

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.tracker_ip, self.tracker_port))
                s.sendall(header_len)
                s.sendall(header_bytes)
                
                received = s.recv(4)
                if not received:
                    return []
                header_len_val = struct.unpack("!I", received)[0]
                
                buffer = b""
                while len(buffer) < header_len_val:
                    chunk = s.recv(min(4096, header_len_val - len(buffer)))
                    if not chunk:
                        break
                    buffer += chunk
                
                if not buffer:
                    return []
                    
                header_data = buffer.decode("utf-8")
                header = json.loads(header_data)
                return header
        except:
            return []

    def preallocate_file(self, filename, size):
        if os.path.exists(filename):
            return
        with open(filename, "wb") as f:
            f.truncate(size)

    # def save_progress(self, filename, bitfield):
    #     with self.lock:
    #         with open(filename + ".meta", "w") as f:
    #             json.dump(bitfield, f)
    def mark_piece_complete(self,filename,piece_idx):
        print("print entered")
        self.bitfield[piece_idx] = 1
        with open(filename + ".meta", "w") as f:
            json.dump(self.bitfield,f)
        print("print closed")
    def load_progress(self, filename, total_pieces):
        meta_file = filename + ".meta"
        if os.path.exists(meta_file):
            with open(meta_file, "r") as f:
                self.bitfield = json.load(f)
        else:
            self.bitfield = [0] * total_pieces
        return self.bitfield

    # def receive_file(self, file_name):
    #     received_data_from_tracker = self.lookup_from_tracker(file_name)
    #     if not received_data_from_tracker:
    #         print("File not found on tracker.")
    #         return

    #     host = received_data_from_tracker[0][0]
    #     port = received_data_from_tracker[0][1]

    #     try:
    #         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #             s.connect((host, port))
                
    #             header = {"action": "HELLO"}
    #             self._send_header(s, header)

    #             received = s.recv(4)
    #             if not received: return
    #             header_len = struct.unpack("!I", received)[0]
    #             header_data = s.recv(header_len).decode("utf-8")
    #             header = json.loads(header_data)

    #             if header["action"] == "READY":
    #                 header = {
    #                     "action": "FILE",
    #                     "name": file_name
    #                 }
    #                 self._send_header(s, header)

    #                 received = s.recv(4)
    #                 if not received: return
    #                 header_len = struct.unpack("!I", received)[0]
    #                 header_data = s.recv(header_len).decode("utf-8")
    #                 header = json.loads(header_data)

    #                 file_name = header["name"]
    #                 file_size = header["size"]

    #                 total_pieces = math.ceil(file_size / self.piece_size)
    #                 self.preallocate_file(file_name, file_size)
    #                 self.load_progress(file_name, total_pieces)

    #                 with open(file_name, "r+b") as f:
    #                     for i in range(total_pieces):
    #                         if self.bitfield[i] == 1:
    #                             continue
                            
    #                         header = {
    #                             "name": file_name,
    #                             "piece_idx": i,
    #                             "piece_size": self.piece_size
    #                         }
    #                         self._send_header(s, header)

    #                         buffer = b""
    #                         expected_size = min(self.piece_size, file_size - (i * self.piece_size))
    #                         while len(buffer) < expected_size:
    #                             chunk = s.recv(min(4096, expected_size - len(buffer)))
    #                             if not chunk:
    #                                 break
    #                             buffer += chunk
                            
    #                         f.seek(i * self.piece_size)
    #                         f.write(buffer)
    #                         self.mark_piece_complete(file_name,i)
    #                         print(f"Downloaded piece {i}/{total_pieces}")

    #                 if all(self.bitfield):
    #                     if os.path.exists(file_name + ".meta"):
    #                         os.remove(file_name + ".meta")
    #                         print(f"\nSuccess! {file_name} is complete.")
    #                 else:
    #                     print("Download incomplete")
    #             else:
    #                 print("Handshake failed")
    #     except Exception as e:
    #         print(f"Error during download: {e}")
    
    def _download_worker(self,host,port,filename,pieces_to_get,filesize):
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM)as s:
                s.connect((host,port))
                header = {
                    "action":"HELLO"
                }
                self._send_header(s,header)
                received = s.recv(4)
                if not received:return
                header_len = struct.unpack("!I",received)[0]
                header_data = s.recv(header_len).decode("utf-8")
                header = json.loads(header_data)

                if header["action"] == "READY":
                    header = {
                        "action":"FILE",
                        "name": filename
                    }
                    self._send_header(s,header)
                    for piece in pieces_to_get:
                        header = {"name": filename, "piece_idx": piece, "piece_size": self.piece_size}
                        self._send_header(s, header)
                        buffer = b""
                        expected_size = min(self.piece_size, filesize - (piece * self.piece_size))
                        while len(buffer) < expected_size:
                            chunk = s.recv(min(4096, expected_size - len(buffer)))
                            if not chunk: break
                            buffer += chunk
                        if len(buffer) == expected_size:
                            with self.lock:
                                with open(filename, "r+b") as f:
                                    f.seek(piece * self.piece_size)
                                    f.write(buffer)
                                self.mark_piece_complete(filename, piece)
                        else:
                            print(f"Warning: Piece {piece} was incomplete. Skipping.")
                            
                        print(f"Piece {piece} from {host} completed")
                else:
                    return

        except Exception as e:
            print(f"Worker for {host} failed: {e}")
        

    def _receive_file_swarm(self,filename):
        print("receive file swarm")
        receive_all_hosts = self.lookup_from_tracker(filename)
        
        if not receive_all_hosts:
            print("No file is present on the tracker")
            return
        fsize = receive_all_hosts["size"]
        fhash = receive_all_hosts["hash"]
        peers = receive_all_hosts["peers"]
        total_pieces = math.ceil(fsize/self.piece_size)
        self.preallocate_file(filename,fsize)
        self.load_progress(filename,total_pieces)
        needed_pieces = [i for i,val in enumerate(self.bitfield) if val == 0]

        chunk_size = math.ceil(len(needed_pieces)/len(peers))
        threads = []
        for idx,peer in enumerate(peers):
            start = idx*chunk_size
            end = start + chunk_size
            assigned_portion = needed_pieces[start:end]
            t = threading.Thread(target=self._download_worker,args=(peer[0],peer[1],filename,assigned_portion,fsize))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        print("Sworm download complete")
        # verification of integrity
        self.verify_client_integrity(filename,fhash)
        if all(self.bitfield):
            os.remove(filename+".meta")
            print("metadata file removed")
    def _send_header(self, sock, header):
        header_bytes = json.dumps(header).encode("utf-8")
        header_len = struct.pack("!I", len(header_bytes))
        sock.sendall(header_len)
        sock.sendall(header_bytes)

def client_node(piece_size):
    client = ClientNode(piece_size)
    client.start()