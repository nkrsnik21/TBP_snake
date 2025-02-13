from ZODB import FileStorage, DB
import pickle
import transaction

class UserProfile:
    def __init__(self, username):
        self.username = username
        self.highscore = 0

    def update_score(self, score):
        if score > self.highscore:
            self.highscore = score

class SnakeGameDatabase:
    def __init__(self, db_file="snake_game_data.fs"):
        self.storage = FileStorage.FileStorage(db_file)
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root
        self.initialize_database()

    def initialize_database(self):
        if not hasattr(self.root, 'profiles'):
            self.root.profiles = {}
        if not hasattr(self.root, 'scores'):
            self.root.scores = []

        transaction.commit()

    def get_or_create_user(self, username):
        if username not in self.root.profiles:
            self.root.profiles[username] = UserProfile(username)
        return self.root.profiles[username]

    def update_user_score(self, username, score):
        user = self.get_or_create_user(username)
        user.update_score(score)
        self.update_scores(user)
        transaction.commit()

    def update_scores(self, user):
        # izbaci vec prisutan ili replicirajuci rezultat
        self.root.scores = [entry for entry in self.root.scores if entry[0] != user.username]

        # dodaj azuriran rezultat usera
        self.root.scores.append((user.username, user.highscore))

        # uzlazno sortiranje rezultata
        self.root.scores = sorted(self.root.scores, key=lambda x: x[1], reverse=True) 

        # zadrzava samo 5 rezultata
        if len(self.root.scores) > 5:
            self.root.scores = self.root.scores[:5]

    def get_top_scores(self):
        # vraca 5 rezultata
        return [f"{user} - {score}" for user, score in self.root.scores]

    def close(self):
        self.connection.close()
        self.db.close()

if __name__ == "__main__":
    db = SnakeGameDatabase()

    # primjer usera i rezultata:
    db.update_user_score("Player1", 150)
    db.update_user_score("Player2", 200)
    db.update_user_score("Player3", 180)
    db.update_user_score("Player4", 220)
    db.update_user_score("Player5", 170)
    db.update_user_score("Player6", 190)  #igrac1 postavlja se na vrh

   #ispis top 5 rezultata
    top_scores = db.get_top_scores()
    print("Top 5 Scores:")
    for score in top_scores:
        print(score)
    db.close()
