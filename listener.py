import socket

def connect_to_socket(host='localhost', port=5000):
    """Connect to a socket server"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"Connected to {host}:{port}")
        return client_socket
    except ConnectionRefusedError:
        print("Connection refused. Make sure the server is running.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    sock = connect_to_socket()
    if sock:
        try:
            # Send/receive data
            sock.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()