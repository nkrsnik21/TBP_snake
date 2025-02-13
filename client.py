import pygame
import random
import socket
import pickle
import sys

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WIDTH, HEIGHT = 600, 800
BLOCK_SIZE = 20
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
FONT = pygame.font.Font(None, 36)
INPUT_BOX_COLOR = (50, 50, 50)
INPUT_BOX_HIGHLIGHT_COLOR = (0, 200, 255)


class SnakeGame:
    def __init__(self):
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = (BLOCK_SIZE, 0)
        self.food = self.generate_food()
        self.score = 0

    def generate_food(self):
        """Generates food that does not spawn on the edges of the screen."""
        while True:
            food_x = random.randrange(1, (WIDTH // BLOCK_SIZE) - 1) * BLOCK_SIZE
            food_y = random.randrange(1, (HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE
            # nema preklapanja hrane sa zmijom
            if (food_x, food_y) not in self.snake:
                return (food_x, food_y)

    def update(self):
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # zid ili zmija kraj igre
        if new_head in self.snake or new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
            return False

        self.snake = [new_head] + self.snake[:-1]

        if new_head == self.food:
            self.snake.append(self.snake[-1])  # zmija se poveća
            self.food = self.generate_food()  # nova hrana
            self.score += 1

        return True

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)

        # dizajn zmije
        for segment in self.snake:
            pygame.draw.rect(screen, GREEN, pygame.Rect(segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

        # dizajn hrane
        pygame.draw.circle(screen, RED, (self.food[0] + BLOCK_SIZE // 2, self.food[1] + BLOCK_SIZE // 2), BLOCK_SIZE // 2)

        # Prikaz rezultata
        score_text = FONT.render(f"Rezultat: {self.score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

        pygame.display.update()

# povezivanje sa serverom
def connect_to_server(username):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5555))
        client.send(username.encode("utf-8"))
        
        highscore = pickle.loads(client.recv(1024))
        print(f"Your current high score: {highscore}")
        return client
    except socket.error as e:
        print(f"Connection error: {e}")
        return None

def reconnect_to_server(username):
    client = connect_to_server(username)
    if not client:
        print("Unable to reconnect to server.")
    return client

def show_game_over_screen(screen, score, top_scores):
    screen.fill(BACKGROUND_COLOR)


    game_over_text = FONT.render("Kraj igre!", True, TEXT_COLOR)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
    
    score_text = FONT.render(f"Tvoj rezultat: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 50))
    
    restart_text = FONT.render("Pritisni Enter za ponovnu igru ili Q za izlaz", True, TEXT_COLOR)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
    
    top_scores_text = FONT.render("Top 5:", True, TEXT_COLOR)
    top_scores_x = WIDTH // 4
    screen.blit(top_scores_text, (top_scores_x - top_scores_text.get_width() // 2, HEIGHT // 1.3))
    
    leaderboard_y = HEIGHT // 1.50
    row_height = 30

    if len(top_scores) == 0:
        top_scores = ["No scores yet"]
    
    for i, score in enumerate(top_scores[:5]):
        score_line = FONT.render(f"{i + 1}. {score}", True, TEXT_COLOR)

        if i % 2 == 0:
            row_color = (40, 40, 40)
        else:
            row_color = (60, 60, 60)

        score_x = WIDTH // 1.5
        pygame.draw.rect(screen, row_color, pygame.Rect(score_x - 150, leaderboard_y + i * row_height, 300, row_height))
        screen.blit(score_line, (score_x - score_line.get_width() // 2, leaderboard_y + i * row_height))

    pygame.display.update()

    waiting_for_restart = True
    while waiting_for_restart:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting_for_restart = False
                elif event.key == pygame.K_q:
                    return False
    return True




def show_input_screen(screen):
    username = ''
    input_active = True
    input_box = pygame.Rect(WIDTH // 4, HEIGHT // 2, WIDTH // 2, 40)
    cursor_color = INPUT_BOX_HIGHLIGHT_COLOR
    input_box_color = INPUT_BOX_COLOR

    while input_active:
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                input_active = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode

        txt_surface = FONT.render(username, True, TEXT_COLOR)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, input_box_color, input_box, 2)
        pygame.draw.rect(screen, cursor_color, pygame.Rect(input_box.x + txt_surface.get_width() + 5, input_box.y + 5, 2, 30))

        instructions_text = FONT.render("Unesite svoje korisničko ime", True, TEXT_COLOR)
        screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, HEIGHT // 4))

        pygame.display.update()

    return username

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    username = show_input_screen(screen)

    client = connect_to_server(username)
    if not client:
        return

    running = True
    while running:
        game = SnakeGame()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        game.direction = (0, -BLOCK_SIZE)
                    elif event.key == pygame.K_DOWN:
                        game.direction = (0, BLOCK_SIZE)
                    elif event.key == pygame.K_LEFT:
                        game.direction = (-BLOCK_SIZE, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.direction = (BLOCK_SIZE, 0)
                    elif event.key == pygame.K_q:
                        running = False
                        break

            if not game.update():
                print(f"Game Over! Your score: {game.score}")
                client.send(pickle.dumps(game.score))

                try:
                    top_scores = pickle.loads(client.recv(4096))
                    show_game_over_screen(screen, game.score, top_scores)
                except socket.error as e:
                    print(f"Socket error: {e}")
                    client = reconnect_to_server(username)

                waiting_for_restart = True
                while waiting_for_restart:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            waiting_for_restart = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                waiting_for_restart = False
                            elif event.key == pygame.K_q:  
                                running = False
                                waiting_for_restart = False
                    if not show_game_over_screen(screen, game.score, top_scores):
                            running = False
                    break

                #pygame.time.wait(2000)

                client = reconnect_to_server(username)
                if not client:
                    running = False
                break

            game.draw(screen)
            clock.tick(15)

    client.close()
    pygame.quit() 
    sys.exit() 

if __name__ == "__main__":
    main()
