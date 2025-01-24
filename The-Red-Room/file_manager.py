import os
import subprocess
import pygame
import sys

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FONT_SIZE = 24
MARGIN = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Directory Browser")
font = pygame.font.Font(None, FONT_SIZE)

# Track history for back navigation
history = []

def draw_text(text, position, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def list_directory(path):
    contents = []
    try:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            contents.append((entry, full_path))
    except PermissionError:
        print(f"Access denied to: {path}")
    except Exception as e:
        print(f"Error accessing {path}: {e}")
    return contents

def execute_file(file_path):
    if os.path.isfile(file_path):
        try:
            subprocess.Popen([file_path], shell=True)
        except Exception as e:
            print(f"Error executing file: {e}")

def main(directory):
    running = True
    contents = list_directory(directory)
    selected_index = 0

    while running:
        screen.fill(BLACK)

        # Draw directory contents
        for index, (name, path) in enumerate(contents):
            y_position = index * (FONT_SIZE + MARGIN)
            if index == selected_index:
                pygame.draw.rect(screen, GRAY, (0, y_position, WINDOW_WIDTH, FONT_SIZE + MARGIN))
                draw_text(name, (MARGIN, y_position), BLACK)  # Highlighted text in black
            else:
                draw_text(name, (MARGIN, y_position), RED)  # Non-highlighted text in red

        # Draw back button
        if history:
            draw_text("Back", (MARGIN, WINDOW_HEIGHT - FONT_SIZE - MARGIN), RED)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and selected_index > 0:
                    selected_index -= 1
                elif event.key == pygame.K_DOWN and selected_index < len(contents) - 1:
                    selected_index += 1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_RETURN:  # Enter the selected folder or execute file
                    selected_item = contents[selected_index]
                    _, path = selected_item
                    if os.path.isdir(path):
                        history.append(directory)  # Save current directory to history
                        contents = list_directory(path)
                        selected_index = 0  # Reset selection
                    elif os.path.isfile(path):
                        execute_file(path)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_BACKSPACE:  # Go back to previous directory
                    if history:
                        directory = history.pop()  # Go back to previous directory
                        contents = list_directory(directory)
                        selected_index = 0  # Reset selection

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    start_directory = "PATH"
    main(start_directory)
