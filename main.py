from client import client_node
from server import server_node
import threading

assets_path = "/home/abinash/Documents/python/small projects/Testing 2/assets"
PIECE_SIZE = 1024 * 64

if __name__ == "__main__":
    server_thread = threading.Thread(target=server_node, args=(assets_path,), daemon=True)
    server_thread.start()

    client_node(PIECE_SIZE)