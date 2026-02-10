# P2P File Sharing System

A decentralized Peer-to-Peer (P2P) file sharing application built with Python. This system allows nodes to share files directly with each other, utilizing a central tracker for peer discovery and a swarm downloading mechanism for efficient file transfer.

## Features

-   **Decentralized File Sharing:** Share and download files directly between peers without passing through a central server for data transfer.
-   **Centralized Tracker:** A lightweight tracker server that manages peer discovery and file locations.
-   **Swarm Downloading:** Downloads files in parallel chunks from multiple peers simultaneously, increasing download speeds and redundancy.
-   **Data Integrity:** Verifies downloaded files using SHA-256 hashing to ensure data corruption-free transfers.
-   **Resumable Downloads:** Tracks download progress, allowing for recovery of interrupted downloads (via `.meta` files).
-   **Automatic Announcement:** Nodes automatically announce their available files to the tracker upon startup.

## Architecture

The system consists of three main components:

1.  **Tracker (`tracker.py`):**
    -   Maintains a registry of files and the peers (IP and Port) hosting them.
    -   Handles `ANNOUNCE` messages from peers to register files.
    -   Handles `LOOKUP` requests from clients to find peers for a specific file.
    -   Runs on port `65000` by default.

2.  **Server Node (`server.py`):**
    -   Runs on each peer to serve files to other peers.
    -   Scans a designated `assets` directory and calculates SHA-256 hashes for all files.
    -   Announces the file list to the Tracker.
    -   listens for incoming connections and serves file chunks upon request.
    -   Runs on port `64500` by default.

3.  **Client Node (`client.py`):**
    -   Allows users to request files.
    -   Queries the Tracker to find peers hosting the desired file.
    -   Connects to multiple peers simultaneously to download different pieces of the file (Swarm Download).
    -   Assembles the pieces and verifies the final file integrity.

## Prerequisites

-   Python 3.x
-   Standard Python libraries: `socket`, `threading`, `json`, `struct`, `os`, `hashlib`, `math`

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Configuration:**
    -   Open `main.py` and modify the `assets_path` variable to point to the directory containing the files you want to share.
        ```python
        # main.py
        assets_path = "/path/to/your/assets_directory" 
        ```
    -   Ensure `tracker.py` is running on a reachable IP (default `127.0.0.1` for local testing). If running on different machines, update `self.tracker_ip` in `client.py` and `server.py`.

## Usage

To run the system, you must first start the tracker, and then start the peer nodes.

### 1. Start the Tracker
Open a terminal and run:
```bash
python tracker.py
```
*The tracker must be running before any nodes can connect.*

### 2. Start a Peer Node
Open a new terminal and run:
```bash
python main.py
```
This script acts as both a server (sharing files from your `assets` path) and a client (allowing you to download files).

### 3. Download a File
Once the `main.py` script is running, you will see a prompt:
```text
Enter the filename you want to download (or 'q' to quit):
```
-   Type the name of a file (e.g., `video.mp4`) that is available on another peer's `assets` directory.
-   Press **Enter**.
-   The client will query the tracker, connect to available peers, and start the swarm download.

## Project Structure

-   `main.py`: Entry point. Starts both the Server and Client threads.
-   `tracker.py`: Central server for peer discovery.
-   `server.py`: Handles file serving and announcing to the tracker.
-   `client.py`: Handles file downloading and logic for swarm transfer.
-   `utils.py`: Helper functions (if any).
-   `assets/`: Directory for storing shared files (customizable).
