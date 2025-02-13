import socket
import pickle
from storage import SnakeGameDatabase

db = SnakeGameDatabase("snake_game_data.fs")

def handle_client(client_socket):
    try:
        username = client_socket.recv(1024).decode("utf-8")
        if not username:
            print("Primljen prazan username, prekidam vezu.")
            return

        user = db.get_or_create_user(username)
        highscore = user.highscore

        client_socket.sendall(pickle.dumps(highscore))
        
        data = client_socket.recv(1024)
        if not data:
            print(f"Korisnik {username} je prekinuo vezu prije slanja rezultata.")
            return
        
        score = pickle.loads(data)

        # ažurira se korisnikov rezultat iz zODB
        db.update_user_score(username, score)

        # 5 update-anih rezultata
        top_scores = db.get_top_scores()

        # slanje klijentu tih 5 rezultata
        client_socket.sendall(pickle.dumps(top_scores))

    except Exception as e:
        print(f"Greška s klijentom {client_socket.getpeername()}: {e}")
    finally:
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen(5)
    print("Server listening on port 5555...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection established with {addr}")
        handle_client(client_socket)

if __name__ == "__main__":
    start_server()
