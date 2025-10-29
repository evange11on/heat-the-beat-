import pygame
import librosa
import numpy as np
import os
import time
import random

# Initialize pygame
pygame.init()

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60
ARROW_SPEED = 5
PERFECT_THRESHOLD = 30  # Increased for better hit detection
GOOD_THRESHOLD = 50     # Increased for better hit detection
HIT_LINE_Y = 500        # Y position of hit line

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
LIGHT_RED = (255, 182, 193)
LIGHT_YELLOW = (255, 255, 224)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hit the beat")
clock = pygame.time.Clock()

# Button class for UI
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        font = pygame.font.SysFont(None, 28)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

# Get all music files in the assets directory
def get_music_files():
    music_files = []
    
    # Create assets directory if it doesn't exist
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Supported audio formats
    supported_formats = ['.mp3', '.wav', '.ogg']
    
    # Find all music files in the assets directory
    for file in os.listdir('assets'):
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext in supported_formats:
            music_files.append(file)
    
    # If no music files found, create a placeholder
    if not music_files:
        print("No music files found in assets folder.")
        print("Please add .mp3, .wav or .ogg files to assets folder.")
        
        # Add a default song option (will use built-in beat pattern)
        music_files.append("Default Beat (Built-in)")
    
    return music_files

# Song selection screen
def song_selection_screen():
    music_files = get_music_files()
    selected_song = None
    
    # Create buttons for each song
    buttons = []
    start_y = 150
    button_height = 50
    button_spacing = 20
    button_width = 500
    
    for i, music_file in enumerate(music_files):
        # Show just the filename without extension for better display
        display_name = os.path.splitext(music_file)[0]
        
        # Truncate if name is too long
        if len(display_name) > 40:
            display_name = display_name[:37] + "..."
            
        btn = Button(
            WIDTH//2 - button_width//2,
            start_y + (button_height + button_spacing) * i,
            button_width,
            button_height,
            display_name,
            DARK_GRAY,
            GRAY
        )
        buttons.append((btn, music_file))
    
    # Add back button
    back_button = Button(30, HEIGHT - 70, 120, 40, "Back", RED, LIGHT_RED)
    
    # Selection screen loop
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # Exit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # Back to main menu
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_click = True
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw title
        font = pygame.font.SysFont(None, 48)
        title = font.render("Select a Song", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Update and draw buttons
        for btn, music_file in buttons:
            btn.update(mouse_pos)
            btn.draw(screen)
            
            # Check for click
            if btn.is_clicked(mouse_pos, mouse_click):
                # If it's the default song, return None
                if music_file == "Default Beat (Built-in)":
                    selected_song = None
                else:
                    selected_song = os.path.join("assets", music_file)
                running = False
        
        # Update and draw back button
        back_button.update(mouse_pos)
        back_button.draw(screen)
        if back_button.is_clicked(mouse_pos, mouse_click):
            return None  # Back to main menu
            
        # Draw instructions
        font = pygame.font.SysFont(None, 24)
        instructions = font.render("Click on a song to play", True, WHITE)
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 50))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return selected_song

# Load assets (create a folder named 'assets' and place your music there)
def load_assets():
    # Create directories if they don't exist
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Let user select a song
    selected_song = song_selection_screen()
    
    # If the user selected a song, return it
    if selected_song:
        return selected_song
    
    # If no song was selected or no music files found, use default
    print("Using a built-in beat pattern for now")
    return None

# Arrow class for falling arrows
class Arrow:
    def __init__(self, direction, spawn_time):
        self.direction = direction
        self.spawn_time = spawn_time
        self.y = 0
        self.width = 50
        self.height = 50
        
        # Set x position based on direction
        if direction == 'left':
            self.x = 200
            self.color = BLUE
            self.light_color = LIGHT_BLUE
        elif direction == 'up':
            self.x = 300
            self.color = GREEN
            self.light_color = LIGHT_GREEN
        elif direction == 'down':
            self.x = 400
            self.color = RED
            self.light_color = LIGHT_RED
        elif direction == 'right':
            self.x = 500
            self.color = YELLOW
            self.light_color = LIGHT_YELLOW
        
        self.hit = False
        self.miss = False
        self.hit_time = 0
        self.hit_type = None  # 'perfect' or 'good'
        
    def update(self, current_time):
        if not self.hit and not self.miss:
            self.y += ARROW_SPEED
            if self.y > HEIGHT:
                self.miss = True
        elif self.hit and current_time - self.hit_time < 0.3:
            # Keep showing hit animation for a short time
            pass
        
    def draw(self, screen):
        if self.hit and time.time() - self.hit_time < 0.3:
            # Draw hit feedback animation
            alpha = 255 - int(255 * (time.time() - self.hit_time) / 0.3)
            if alpha < 0:
                alpha = 0
                
            hit_text = "PERFECT!" if self.hit_type == 'perfect' else "GOOD!"
            hit_color = CYAN if self.hit_type == 'perfect' else GREEN
            font = pygame.font.SysFont(None, 28)
            text = font.render(hit_text, True, hit_color)
            text.set_alpha(alpha)
            screen.blit(text, (self.x, HIT_LINE_Y - 30))
            
            # Draw a fading circle effect
            radius = int(30 * (time.time() - self.hit_time) / 0.3) + 20
            circle_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, (*self.color[:3], alpha), (radius, radius), radius)
            screen.blit(circle_surf, (self.x + self.width//2 - radius, HIT_LINE_Y + self.height//2 - radius))
            
        elif not self.hit and not self.miss:
            # Draw the arrow
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            
            # Draw arrow direction indicator with better visibility
            if self.direction == 'left':
                pygame.draw.polygon(screen, WHITE, [(self.x + 38, self.y + 10), (self.x + 38, self.y + 40), (self.x + 12, self.y + 25)])
                # Draw outline for better visibility
                pygame.draw.polygon(screen, BLACK, [(self.x + 38, self.y + 10), (self.x + 38, self.y + 40), (self.x + 12, self.y + 25)], 2)
            elif self.direction == 'up':
                pygame.draw.polygon(screen, WHITE, [(self.x + 10, self.y + 38), (self.x + 40, self.y + 38), (self.x + 25, self.y + 12)])
                pygame.draw.polygon(screen, BLACK, [(self.x + 10, self.y + 38), (self.x + 40, self.y + 38), (self.x + 25, self.y + 12)], 2)
            elif self.direction == 'down':
                pygame.draw.polygon(screen, WHITE, [(self.x + 10, self.y + 12), (self.x + 40, self.y + 12), (self.x + 25, self.y + 38)])
                pygame.draw.polygon(screen, BLACK, [(self.x + 10, self.y + 12), (self.x + 40, self.y + 12), (self.x + 25, self.y + 38)], 2)
            elif self.direction == 'right':
                pygame.draw.polygon(screen, WHITE, [(self.x + 12, self.y + 10), (self.x + 12, self.y + 40), (self.x + 38, self.y + 25)])
                pygame.draw.polygon(screen, BLACK, [(self.x + 12, self.y + 10), (self.x + 12, self.y + 40), (self.x + 38, self.y + 25)], 2)

# Function to analyze beats in the music
def analyze_music(music_path):
    try:
        # Load the audio file and calculate tempo and beat frames
        y, sr = librosa.load(music_path)
        
        # Get onset frames (when there's a note/beat)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
        
        # Convert frames to time (in seconds)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
        print(f"Detected {len(onset_times)} beats")
        return onset_times
    except Exception as e:
        print(f"Error analyzing music: {e}")
        # Return some dummy beats for testing if music analysis fails
        return np.linspace(1, 60, 30)  # 30 beats over 60 seconds

# Generate arrows based on beats
def generate_arrows(beat_times):
    arrows = []
    directions = ['left', 'up', 'down', 'right']
    
    # Ensure balanced distribution of directions
    direction_counts = {d: 0 for d in directions}
    
    for beat_time in beat_times:
        # Try to balance directions
        if max(direction_counts.values()) > min(direction_counts.values()) + 3:
            # Choose one of the least used directions
            min_count = min(direction_counts.values())
            least_used = [d for d in directions if direction_counts[d] == min_count]
            direction = random.choice(least_used)
        else:
            direction = random.choice(directions)
            
        direction_counts[direction] += 1
        arrows.append(Arrow(direction, beat_time))
    
    return arrows

# Draw the arrow targets at the bottom
def draw_targets(active_key=None):
    # Draw hit line
    pygame.draw.line(screen, WHITE, (150, HIT_LINE_Y), (650, HIT_LINE_Y), 3)
    
    # Draw targets with active highlighting
    left_color = LIGHT_BLUE if active_key == 'left' else BLUE
    up_color = LIGHT_GREEN if active_key == 'up' else GREEN
    down_color = LIGHT_RED if active_key == 'down' else RED
    right_color = LIGHT_YELLOW if active_key == 'right' else YELLOW
    
    # Draw targets
    pygame.draw.rect(screen, left_color, (200, HIT_LINE_Y, 50, 50), 0 if active_key == 'left' else 2)
    pygame.draw.rect(screen, up_color, (300, HIT_LINE_Y, 50, 50), 0 if active_key == 'up' else 2)
    pygame.draw.rect(screen, down_color, (400, HIT_LINE_Y, 50, 50), 0 if active_key == 'down' else 2)
    pygame.draw.rect(screen, right_color, (500, HIT_LINE_Y, 50, 50), 0 if active_key == 'right' else 2)
    
    # Draw direction indicators in targets with better visibility
    pygame.draw.polygon(screen, WHITE, [(235, HIT_LINE_Y + 10), (235, HIT_LINE_Y + 40), (215, HIT_LINE_Y + 25)])
    pygame.draw.polygon(screen, BLACK, [(235, HIT_LINE_Y + 10), (235, HIT_LINE_Y + 40), (215, HIT_LINE_Y + 25)], 2)
    
    pygame.draw.polygon(screen, WHITE, [(310, HIT_LINE_Y + 35), (340, HIT_LINE_Y + 35), (325, HIT_LINE_Y + 15)])
    pygame.draw.polygon(screen, BLACK, [(310, HIT_LINE_Y + 35), (340, HIT_LINE_Y + 35), (325, HIT_LINE_Y + 15)], 2)
    
    pygame.draw.polygon(screen, WHITE, [(410, HIT_LINE_Y + 15), (440, HIT_LINE_Y + 15), (425, HIT_LINE_Y + 35)])
    pygame.draw.polygon(screen, BLACK, [(410, HIT_LINE_Y + 15), (440, HIT_LINE_Y + 15), (425, HIT_LINE_Y + 35)], 2)
    
    pygame.draw.polygon(screen, WHITE, [(515, HIT_LINE_Y + 10), (515, HIT_LINE_Y + 40), (535, HIT_LINE_Y + 25)])
    pygame.draw.polygon(screen, BLACK, [(515, HIT_LINE_Y + 10), (515, HIT_LINE_Y + 40), (535, HIT_LINE_Y + 25)], 2)

# Display hit feedback text
def display_hit_text(hit_type, x, y):
    font = pygame.font.SysFont(None, 36)
    if hit_type == "perfect":
        text = font.render("PERFECT!", True, CYAN)
    elif hit_type == "good":
        text = font.render("GOOD!", True, GREEN)
    else:
        text = font.render("MISS!", True, RED)
    
    screen.blit(text, (x, y))

# Main game function
def main():
    # Create a main menu first
    show_main_menu = True
    
    while show_main_menu:
        # Main menu
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 64)
        title = font.render("Heat the beat", True, WHITE)
        
        # Create menu buttons
        play_button = Button(WIDTH//2 - 150, HEIGHT//2 - 70, 300, 60, "Play", GREEN, LIGHT_GREEN)
        quit_button = Button(WIDTH//2 - 150, HEIGHT//2 + 10, 300, 60, "Quit", RED, LIGHT_RED)
        
        # Draw menu
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  # Exit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Exit game
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_click = True
        
        # Update and draw buttons
        play_button.update(mouse_pos)
        play_button.draw(screen)
        
        quit_button.update(mouse_pos)
        quit_button.draw(screen)
        
        # Handle button clicks
        if play_button.is_clicked(mouse_pos, mouse_click):
            # Get selected song
            music_path = load_assets()
            
            # If a song was selected, start the game
            if music_path is not None or music_path == None:  # None is valid for default beat pattern
                play_game(music_path)
                
        if quit_button.is_clicked(mouse_pos, mouse_click):
            return  # Exit game
            
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

# Play the actual rhythm game with the selected song
def play_game(music_path):
    # Analyze music to get beat times
    beat_times = analyze_music(music_path if music_path else None)
    
    # Generate arrows based on beat times
    arrows = generate_arrows(beat_times)
    
    # Game variables
    score = 0
    combo = 0
    max_combo = 0
    active_key = None
    key_press_time = 0
    
    start_time = time.time()
    song_started = False
    
    # Sound effects for hits
    try:
        hit_sound = pygame.mixer.Sound('assets/hit.wav')
        perfect_sound = pygame.mixer.Sound('assets/perfect.wav')
    except:
        # Create directory for sound effects if it doesn't exist
        hit_sound = None
        perfect_sound = None
    
    # Display song info
    song_name = os.path.basename(music_path) if music_path else "Default Beat Pattern"
    
    # Load the music if available
    if music_path:
        pygame.mixer.music.load(music_path)
    
    running = True
    
    # Welcome screen
    show_welcome = True
    while show_welcome:
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 48)
        title = font.render("Get Ready!", True, WHITE)
        song_title = pygame.font.SysFont(None, 36)
        song_text = song_title.render(f"Song: {song_name}", True, CYAN)
        instructions = pygame.font.SysFont(None, 28)
        inst_text1 = instructions.render("Press the arrow keys to hit the notes when they reach the white line", True, WHITE)
        inst_text2 = instructions.render("Press SPACE to start", True, GREEN)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        screen.blit(song_text, (WIDTH//2 - song_text.get_width()//2, HEIGHT//4 + 60))
        screen.blit(inst_text1, (WIDTH//2 - inst_text1.get_width()//2, HEIGHT//2))
        screen.blit(inst_text2, (WIDTH//2 - inst_text2.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    show_welcome = False
                elif event.key == pygame.K_ESCAPE:
                    return
    
    # Start the music
    if music_path:
        pygame.mixer.music.play()
    song_started = True
    start_time = time.time()
    
    # Main game loop
    while running:
        current_time = time.time() - start_time
        
        # Reset active key after a short time
        if active_key and time.time() - key_press_time > 0.1:
            active_key = None
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                key_hit = None
                if event.key == pygame.K_LEFT:
                    key_hit = 'left'
                elif event.key == pygame.K_UP:
                    key_hit = 'up'
                elif event.key == pygame.K_DOWN:
                    key_hit = 'down'
                elif event.key == pygame.K_RIGHT:
                    key_hit = 'right'
                elif event.key == pygame.K_ESCAPE:
                    running = False
                
                # Update active key for visual feedback
                if key_hit:
                    active_key = key_hit
                    key_press_time = time.time()
                
                # Check if any arrows can be hit - prioritize arrows closest to hit line
                if key_hit:
                    hit_candidates = []
                    for i, arrow in enumerate(arrows):
                        if not arrow.hit and not arrow.miss and arrow.direction == key_hit and abs(arrow.y - HIT_LINE_Y) <= GOOD_THRESHOLD:
                            hit_candidates.append((i, abs(arrow.y - HIT_LINE_Y)))
                    
                    if hit_candidates:
                        # Sort by distance to hit line
                        hit_candidates.sort(key=lambda x: x[1])
                        idx, distance = hit_candidates[0]
                        
                        # Apply hit
                        arrows[idx].hit = True
                        arrows[idx].hit_time = time.time()
                        
                        if distance <= PERFECT_THRESHOLD:
                            arrows[idx].hit_type = 'perfect'
                            score += 100
                            combo += 1
                            if perfect_sound:
                                perfect_sound.play()
                        else:
                            arrows[idx].hit_type = 'good'
                            score += 50
                            combo += 1
                            if hit_sound:
                                hit_sound.play()
                                
                        if combo > max_combo:
                            max_combo = combo
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Update and spawn arrows
        for arrow in arrows:
            if not arrow.miss and current_time >= arrow.spawn_time:
                arrow.update(current_time)
                arrow.draw(screen)
            
            # Check for misses
            if arrow.y > HIT_LINE_Y + GOOD_THRESHOLD and not arrow.hit and not arrow.miss:
                arrow.miss = True
                combo = 0
        
        # Draw the targets with active key highlighting
        draw_targets(active_key)
        
        # Draw the score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        combo_text = font.render(f"Combo: {combo}", True, WHITE)
        screen.blit(score_text, (20, 20))
        screen.blit(combo_text, (20, 60))
        
        # Display song name
        song_font = pygame.font.SysFont(None, 24)
        song_display = song_font.render(f"Song: {song_name}", True, CYAN)
        screen.blit(song_display, (WIDTH - song_display.get_width() - 20, 20))
        
        # Check if song is over
        if current_time > max(beat_times) + 5 and all(arrow.hit or arrow.miss for arrow in arrows):
            running = False
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Game over screen
    show_game_over = True
    while show_game_over:
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 48)
        title = font.render("Game Over", True, WHITE)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        combo_text = font.render(f"Max Combo: {max_combo}", True, WHITE)
        
        # Create buttons
        play_again_button = Button(WIDTH//2 - 150, HEIGHT//2 + 100, 300, 50, "Play Again", GREEN, LIGHT_GREEN)
        main_menu_button = Button(WIDTH//2 - 150, HEIGHT//2 + 160, 300, 50, "Main Menu", BLUE, LIGHT_BLUE)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(combo_text, (WIDTH//2 - combo_text.get_width()//2, HEIGHT//2 + 50))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_game_over = False  # Return to main menu
        
        # Update and draw buttons
        play_again_button.update(mouse_pos)
        play_again_button.draw(screen)
        
        main_menu_button.update(mouse_pos)
        main_menu_button.draw(screen)
        
        # Handle button clicks
        if play_again_button.is_clicked(mouse_pos, mouse_click):
            show_game_over = False
            play_game(music_path)  # Play the same song again
            
        if main_menu_button.is_clicked(mouse_pos, mouse_click):
            show_game_over = False  # Return to main menu
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
