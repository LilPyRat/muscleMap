import socket
import psycopg2

def data_handler(data):
    try:
        connection = psycopg2.connect(
            dbname='DB_muscleMap',
            user='postgres',
            password='pass1234',
            host='localhost',
            port='5432'
        )
        cursor = connection.cursor()
        cursor.execute("INSERT INTO muscle_data (data) VALUES (%s)", (data,))
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error: {e}")


def main():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to a port
    host = 'localhost'
    port = 5000
    server_socket.bind((host, port))
    
    # Listen for incoming connections
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    
    try:
        while True:
            # Accept a connection
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            
            # Receive data
            data = client_socket.recv(1024).decode()
            print(f"Received: {data}")
            
            # Send response
            client_socket.send("Message received".encode())
            data_handler(data)
            client_socket.close()
    except KeyboardInterrupt:
        print("Server shutting down")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()