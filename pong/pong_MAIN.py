import pygame, sys, random, math

# Game Initialization and Management
pygame.init()
WIDTH, HEIGHT = 1280, 700
FONT = pygame.font.SysFont("Consolas", int(WIDTH / 20))
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong!")
CLOCK = pygame.time.Clock()
LEFT_MARGIN = 75

live_ball = False
paused = False  
player_score, opponent_score = 0, 0
ai_difficulty = 0.2
boss_mode = False
# Indices for difficulty settings
difficulty_levels = [0.2, 0.4, 0.6, 0.8, 1.0]
difficulty_index = difficulty_levels.index(ai_difficulty)

# Load Sounds
main_music = 'Games/Pong/srstrnc.wav'
boss_music = 'Games/Pong/boss-music.wav'
point_sfx = pygame.mixer.Sound('Games/Pong/8bit_point_sfx.wav')
current_music = None

def play_music(is_boss_mode):
    """Handle music switching between normal and boss mode"""
    global current_music
    
    # Determine which music track to play
    music_track = boss_music if is_boss_mode else main_music
    
    # Only change the music if it's different from what's currently playing
    if current_music != music_track:
        pygame.mixer.music.stop()  # Stop current music
        pygame.mixer.music.unload()  # Unload current music
        pygame.mixer.music.load(music_track)  # Load new music
        pygame.mixer.music.play(-1)  # Play on loop (-1 means loop indefinitely)
        current_music = music_track

# Paddles
player = pygame.Rect(WIDTH - 30, HEIGHT / 2 - 50, 20, 140)
opponent = pygame.Rect(30, HEIGHT / 2 - 50, 20, 140)

# Paddle properties
PADDLE_ACCELERATION = 1.25
MAX_PADDLE_SPEED = 15
BOSS_PADDLE_SPEED = 20

# Paddle state
player_paddle_speed = 0
opponent_paddle_speed = 0

# Ball
ball = pygame.Rect(WIDTH / 2 - 10, HEIGHT / 2 - 10, 27, 27)

x_speed, y_speed = 20, 20
ball_speed_levels = [6, 8, 10, 12, 14, 16]
ball_speed_index = 4

# Settings for the game
ball_color = "orange"
scoreboard_color = "white"
player_paddle_color = "dodgerblue"
opponent_paddle_color = "tomato"
boss_paddle_color = "red"

# -------------------- START MENU --------------------
def show_start_menu():
    """Displays the start menu and waits for the player to start the game with mouse interaction."""
    global boss_mode, opponent_paddle_color
    
    while True:
        SCREEN.fill("Black")

        # ---------- Text for the menu options ----------
        title_text = FONT.render("Pong!", True, "orange")
        play_text = FONT.render("Play", True, "white")
        boss_text = FONT.render("Boss Mode", True, "red")
        settings_text = FONT.render("Settings", True, "white")

        # Create rectangles for menu options
        qg_rect = play_text.get_rect(topleft=(LEFT_MARGIN, HEIGHT / 2 - 150))
        boss_rect = boss_text.get_rect(topleft=(LEFT_MARGIN, HEIGHT / 2 - 50))
        settings_rect = settings_text.get_rect(topleft=(LEFT_MARGIN, HEIGHT / 2 + 50))

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check hover for Play
        if qg_rect.collidepoint(mouse_x, mouse_y):
            play_text = FONT.render("Play", True, "yellow")
            pygame.draw.rect(SCREEN, "yellow", qg_rect.inflate(20, 10), 3)

        # Check hover for Boss Mode
        if boss_rect.collidepoint(mouse_x, mouse_y):
            boss_text = FONT.render("Boss Mode", True, "yellow")
            pygame.draw.rect(SCREEN, "yellow", boss_rect.inflate(20, 10), 3)

        # Check hover for Settings
        if settings_rect.collidepoint(mouse_x, mouse_y):
            settings_text = FONT.render("Settings", True, "yellow")
            pygame.draw.rect(SCREEN, "yellow", settings_rect.inflate(20, 10), 3)

        # Blit the menu items
        SCREEN.blit(title_text, (LEFT_MARGIN, HEIGHT / 12))
        SCREEN.blit(play_text, qg_rect.topleft)
        SCREEN.blit(boss_text, boss_rect.topleft)
        SCREEN.blit(settings_text, settings_rect.topleft)

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if qg_rect.collidepoint(mouse_x, mouse_y):
                    boss_mode = False
                    opponent_paddle_color = "tomato"
                    play_music(False)  # Start normal music
                    return
                if boss_rect.collidepoint(mouse_x, mouse_y):
                    boss_mode = True
                    opponent_paddle_color = boss_paddle_color
                    play_music(True)  # Start boss music
                    return
                if settings_rect.collidepoint(mouse_x, mouse_y):
                    show_settings_menu()

# -------------------- IN-GAME PAUSE MENU --------------------
def show_pause_menu():
    """Displays the pause menu and allows the player to resume, restart, or return to the main menu."""
    global paused

    pygame.mixer.music.pause()

    while paused:
        SCREEN.fill("Black")

        # ---------- Pause Menu Text ----------
        pause_title = FONT.render("Paused", True, "orange")
        resume_text = FONT.render("Resume Game", True, "white")
        restart_text = FONT.render("Restart Game", True, "white")
        main_menu_text = FONT.render("Return to Main Menu", True, "white")

        # ---------- Create rectangles for menu options to detect hovering ----------
        resume_rect = resume_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 100))
        restart_rect = restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        main_menu_rect = main_menu_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 100))

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Highlight and detect clicks for "Resume Game"
        if resume_rect.collidepoint(mouse_x, mouse_y):
            resume_text = FONT.render("Resume Game", True, "yellow")
            pygame.draw.rect(SCREEN, "yellow", resume_rect.inflate(20, 20), 3)
            if pygame.mouse.get_pressed()[0]:
                paused = False  # Resume the game

        # Highlight and detect clicks for "Restart Game"
        if restart_rect.collidepoint(mouse_x, mouse_y):
            restart_text = FONT.render("Restart Game", True, "yellow")
            pygame.draw.rect(SCREEN, "yellow", restart_rect.inflate(20, 20), 3)
            if pygame.mouse.get_pressed()[0]:
                restart_game()  # Call the restart function
                paused = False  # Unpause the game after restart

        # Highlight and detect clicks for "Return to Main Menu"
        if main_menu_rect.collidepoint(mouse_x, mouse_y):
            main_menu_text = FONT.render("Return to Main Menu", True, "yellow")
            pygame.draw.rect(SCREEN, "yellow", main_menu_rect.inflate(20, 20), 3)
            if pygame.mouse.get_pressed()[0]:
                show_start_menu()  # Function to go back to the main menu

        # Render the pause menu items
        SCREEN.blit(pause_title, (WIDTH / 2 - 100, HEIGHT / 6))
        SCREEN.blit(resume_text, resume_rect.topleft)
        SCREEN.blit(restart_text, restart_rect.topleft)
        SCREEN.blit(main_menu_text, main_menu_rect.topleft)

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not paused:
            pygame.mixer.music.unpause()


# -------------------- SETTINGS MENU --------------------
def show_settings_menu():
    """Displays the settings menu to allow players to adjust options."""
    global ball_color, scoreboard_color, player_paddle_color, opponent_paddle_color, ai_difficulty, difficulty_index, difficulty_levels, LEFT_MARGIN
    global ball_speed_index, ball_speed_levels, x_speed, y_speed

    colors = ["aqua", "blue", "brown", "coral", "crimson", "cyan", "fuchsia", "gold", 
              "gray", "greenyellow", "indigo", "lavender", "lime", "moccasin", "navy", "orange", 
              "plum", "purple", "red", "salmon", "silver", "springgreen", "tomato", "turquoise", "violet", "khaki1", 
              "white", "yellow", "dodgerblue"]

    # Indices for selected colors
    ball_color_index = colors.index(ball_color)
    scoreboard_color_index = colors.index(scoreboard_color)
    player_paddle_color_index = colors.index(player_paddle_color)
    opponent_paddle_color_index = colors.index(opponent_paddle_color)

    mouse_released = True  # Track mouse release to prevent continuous cycling

    # Constant vertical offsets for spacing menu items
    VERTICAL_SPACING = 75
    START_Y = HEIGHT / 2 - 225

    # Create random button text and position
    random_button_text = FONT.render("Randomize Colors", True, "white")
    random_button_rect = random_button_text.get_rect(topright=(WIDTH - 40, 40))

    # Wait for the mouse button to be released
    while pygame.mouse.get_pressed()[0]:  # Wait for the mouse button to be released before proceeding
        pygame.event.pump()  # Keep processing events to avoid freezing

    while True:
        SCREEN.fill("Black")

        # Settings title
        settings_title = FONT.render("Settings", True, "orange")

        # Render menu items and get their rects
        ball_color_rect = render_menu_item("Ball Color: ", colors[ball_color_index], (LEFT_MARGIN, START_Y))
        scoreboard_color_rect = render_menu_item("Scoreboard Color: ", colors[scoreboard_color_index], (LEFT_MARGIN, START_Y + VERTICAL_SPACING))
        player_paddle_color_rect = render_menu_item("Player Paddle Color: ", colors[player_paddle_color_index], (LEFT_MARGIN, START_Y + 2 * VERTICAL_SPACING))
        opponent_paddle_color_rect = render_menu_item("Opponent Paddle Color: ", colors[opponent_paddle_color_index], (LEFT_MARGIN, START_Y + 3 * VERTICAL_SPACING))
        ai_difficulty_rect = render_menu_item("AI Difficulty: ", difficulty_levels[difficulty_index], (LEFT_MARGIN, START_Y + 4 * VERTICAL_SPACING))
        ball_speed_rect = render_menu_item("Ball Speed: ", ball_speed_levels[ball_speed_index], (LEFT_MARGIN, START_Y + 5 * VERTICAL_SPACING))
        back_rect = render_text_item("Back to Menu", (LEFT_MARGIN, START_Y + 6 * VERTICAL_SPACING))

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Draw random button
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if random_button_rect.collidepoint(mouse_x, mouse_y):
            random_button_text = FONT.render("Randomize Colors", True, "yellow")
            pygame.draw.rect(SCREEN, "yellow", random_button_rect.inflate(20, 20), 3)
            if pygame.mouse.get_pressed()[0] and mouse_released:
                # Randomize colors but ensure they're all different
                available_colors = colors.copy()
                # Randomize ball color
                ball_color_index = colors.index(random.choice(available_colors))
                available_colors.remove(colors[ball_color_index])
                # Randomize scoreboard color
                scoreboard_color_index = colors.index(random.choice(available_colors))
                available_colors.remove(colors[scoreboard_color_index])
                # Randomize player paddle color
                player_paddle_color_index = colors.index(random.choice(available_colors))
                available_colors.remove(colors[player_paddle_color_index])
                # Randomize opponent paddle color
                opponent_paddle_color_index = colors.index(random.choice(available_colors))
                mouse_released = False
        
        SCREEN.blit(random_button_text, random_button_rect)

        # Handle input and highlighting for each setting
        ball_color_index, mouse_released = handle_menu_input(ball_color_rect, ball_color_index, colors, mouse_x, mouse_y, mouse_released)
        scoreboard_color_index, mouse_released = handle_menu_input(scoreboard_color_rect, scoreboard_color_index, colors, mouse_x, mouse_y, mouse_released)
        player_paddle_color_index, mouse_released = handle_menu_input(player_paddle_color_rect, player_paddle_color_index, colors, mouse_x, mouse_y, mouse_released)
        opponent_paddle_color_index, mouse_released = handle_menu_input(opponent_paddle_color_rect, opponent_paddle_color_index, colors, mouse_x, mouse_y, mouse_released)
        difficulty_index, mouse_released = handle_menu_input(ai_difficulty_rect, difficulty_index, difficulty_levels, mouse_x, mouse_y, mouse_released)
        ball_speed_index, mouse_released = handle_menu_input(ball_speed_rect, ball_speed_index, ball_speed_levels, mouse_x, mouse_y, mouse_released)

        # Highlight and handle "Back to Menu" button
        if back_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(SCREEN, "yellow", back_rect.inflate(20, 20), 3)
            if pygame.mouse.get_pressed()[0] and mouse_released:
                # Save settings and go back to the main menu
                ball_color = colors[ball_color_index]
                scoreboard_color = colors[scoreboard_color_index]
                player_paddle_color = colors[player_paddle_color_index]
                opponent_paddle_color = colors[opponent_paddle_color_index]
                ai_difficulty = difficulty_levels[difficulty_index]  # Save AI difficulty
                #x_speed, y_speed = ball_speed_levels[ball_speed_index]
                return

        # Reset mouse_released when the mouse button is released
        if not pygame.mouse.get_pressed()[0]:
            mouse_released = True

        # Render the title
        SCREEN.blit(settings_title, (LEFT_MARGIN, START_Y - 80))

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# Helper function to render a menu item
def render_menu_item(prefix, value, position):
    text_prefix = FONT.render(prefix, True, "white")
    text_value = FONT.render(str(value), True, value if isinstance(value, str) else "yellow")
    rect_prefix = text_prefix.get_rect(topleft=position)
    SCREEN.blit(text_prefix, position)
    SCREEN.blit(text_value, (rect_prefix.right + 10, rect_prefix.top))
    return rect_prefix

# Helper function to render a simple text item like "Back to Menu"
def render_text_item(text, position):
    rendered_text = FONT.render(text, True, "white")
    rect = rendered_text.get_rect(topleft=position)
    SCREEN.blit(rendered_text, position)
    return rect

# Function to handle menu input and return the updated index
def handle_menu_input(item_rect, current_index, item_list, mouse_x, mouse_y, mouse_released):
    if item_rect.collidepoint(mouse_x, mouse_y):
        highlight_rect = pygame.Rect(
            item_rect.x - 10,
            item_rect.y - 10,
            item_rect.width + FONT.size(str(item_list[current_index]))[0] + 35,
            item_rect.height + 15
        )
        pygame.draw.rect(SCREEN, "yellow", highlight_rect, 3)

        # Detect mouse click (button pressed and released) and cycle through items
        if pygame.mouse.get_pressed()[0]:  # Mouse is currently pressed
            if mouse_released:  # Check if this is a fresh click (not held down)
                current_index = (current_index + 1) % len(item_list)  # Cycle through items
                mouse_released = False  # Prevent further changes until the mouse is released
        else:
            mouse_released = True  # Reset the flag when the mouse is released

    return current_index, mouse_released  # Return both the index and the updated state of mouse_released

# -------------------- Helper Functions --------------------
def reset_ball(starting_player='player'):
    """Reset the ball position and speed based on the player who starts it."""
    global ball, x_speed, y_speed
    
    # Position the ball at the center of the appropriate paddle
    if starting_player == 'player':
        ball.centerx = player.centerx - ball.width  # Start at player's paddle
        ball.centery = player.centery
    else:
        ball.centerx = opponent.centerx + ball.width  # Start at opponent's paddle
        ball.centery = opponent.centery

    # Set initial speed (faster in boss mode)
    base_speed = ball_speed_levels[ball_speed_index]
    if boss_mode:
        base_speed *= 1.3  # 30% faster in boss mode

    # Set direction based on starting player
    if starting_player == 'player':
        x_speed = -abs(base_speed)  # Move towards opponent
    else:
        x_speed = abs(base_speed)   # Move towards player
    
    # Add more vertical variation in boss mode
    if boss_mode:
        y_speed = random.uniform(-base_speed * 0.8, base_speed * 0.8)
    else:
        y_speed = random.choice([base_speed / 2, -base_speed / 2])

def draw_screen():
    SCREEN.fill("Black")
    pygame.draw.line(SCREEN, scoreboard_color, (WIDTH / 2, 0), (WIDTH / 2, HEIGHT))  # Scoreboard line
    pygame.draw.rect(SCREEN, player_paddle_color, player)
    pygame.draw.rect(SCREEN, opponent_paddle_color, opponent)
    pygame.draw.ellipse(SCREEN, ball_color, ball)
    player_score_text = FONT.render(str(player_score), True, scoreboard_color)
    opponent_score_text = FONT.render(str(opponent_score), True, scoreboard_color)
    SCREEN.blit(player_score_text, (WIDTH / 2 + 40, HEIGHT / 8))
    SCREEN.blit(opponent_score_text, (WIDTH / 2 - 80, HEIGHT / 8))

def restart_game():
    global player_score, opponent_score, paused, boss_mode
    player_score, opponent_score = 0, 0
    reset_ball()
    paused = False
    # Restart appropriate music
    play_music(boss_mode)


# Game Logic
def handle_ball_movement():
    """
    Updates ball position and handles wall collisions with classic pong physics.
    """
    global x_speed, y_speed, player_score, opponent_score

    # Move the ball
    ball.x += x_speed
    ball.y += y_speed
    
    # Perfect elastic collisions with walls (no dampening)
    if ball.top <= 0:
        ball.top = 0
        y_speed = abs(y_speed)  # Reverse direction with full energy
    elif ball.bottom >= HEIGHT:
        ball.bottom = HEIGHT
        y_speed = -abs(y_speed)  # Reverse direction with full energy

    # Scoring logic
    if ball.left <= 0:
        player_score += 1
        pygame.mixer.Sound.play(point_sfx)
        reset_ball('player')
    elif ball.right >= WIDTH:
        opponent_score += 1
        pygame.mixer.Sound.play(point_sfx)
        reset_ball('opponent')

    # Check for paddle collisions
    if ball.colliderect(player):
        check_ball_paddle_collision(ball, player)
    elif ball.colliderect(opponent):
        check_ball_paddle_collision(ball, opponent)

def handle_paddle_movement():
    global player_paddle_speed, opponent_paddle_speed

    keys = pygame.key.get_pressed()

    # Player paddle movement
    if keys[pygame.K_UP]:
        player_paddle_speed = max(player_paddle_speed - PADDLE_ACCELERATION, -MAX_PADDLE_SPEED)  # Accelerate up
    elif keys[pygame.K_DOWN]:
        player_paddle_speed = min(player_paddle_speed + PADDLE_ACCELERATION, MAX_PADDLE_SPEED)  # Accelerate down
    else:
        # Decelerate when no key is pressed
        if player_paddle_speed > 0:
            player_paddle_speed = max(player_paddle_speed - PADDLE_ACCELERATION, 0)
        elif player_paddle_speed < 0:
            player_paddle_speed = min(player_paddle_speed + PADDLE_ACCELERATION, 0)

    # Move player paddle
    player.y += player_paddle_speed

    # Prevent paddle from going out of bounds
    if player.top < 0:
        player.top = 0
    if player.bottom > HEIGHT:
        player.bottom = HEIGHT

    # Opponent paddle movement (AI or similar logic)
    if opponent_paddle_speed > 0:
        opponent.y += opponent_paddle_speed

    # Update opponent paddle movement logic (if it's AI, follow the ball, etc.)
    if ball.centery > opponent.centery:
        opponent_paddle_speed = min(opponent_paddle_speed + PADDLE_ACCELERATION, MAX_PADDLE_SPEED)  # Accelerate down
    elif ball.centery < opponent.centery:
        opponent_paddle_speed = max(opponent_paddle_speed - PADDLE_ACCELERATION, -MAX_PADDLE_SPEED)  # Accelerate up
    else:
        # Decelerate when not moving
        if opponent_paddle_speed > 0:
            opponent_paddle_speed = max(opponent_paddle_speed - PADDLE_ACCELERATION, 0)
        elif opponent_paddle_speed < 0:
            opponent_paddle_speed = min(opponent_paddle_speed + PADDLE_ACCELERATION, 0)

    # Move opponent paddle
    opponent.y += opponent_paddle_speed

    # Prevent opponent paddle from going out of bounds
    if opponent.top < 0:
        opponent.top = 0
    if opponent.bottom > HEIGHT:
        opponent.bottom = HEIGHT

def check_ball_paddle_collision(ball, paddle):
    """
    Handles ball-paddle collisions with realistic physics.
    The return angle is calculated based on where the ball hits the paddle.
    """
    global x_speed, y_speed
    
    if ball.colliderect(paddle):
        # Determine which side of the paddle was hit
        if paddle == player:
            ball.right = player.left
        else:
            ball.left = opponent.right
            
        # Calculate relative intersection point
        relative_intersect_y = (paddle.centery - ball.centery) / (paddle.height / 2)
        
        # Normalize between -1 and 1
        normalized_intersect = min(max(relative_intersect_y, -1.0), 1.0)
        
        # Maximum return angle (in radians)
        max_bounce_angle = math.pi / 3  # 60 degrees
        
        # Calculate return angle
        bounce_angle = normalized_intersect * max_bounce_angle
        
        # Calculate new velocity
        speed = math.sqrt(x_speed * x_speed + y_speed * y_speed)
        speed *= 1.03  # Increase speed slightly with each hit
        
        # Ensure the ball moves in the correct direction after collision
        if paddle == player:
            direction = -1
        else:
            direction = 1
            
        # Calculate new x and y speeds based on the bounce angle
        x_speed = direction * abs(speed * math.cos(bounce_angle))
        y_speed = speed * -math.sin(bounce_angle)
        
        # Ensure minimum vertical movement to prevent horizontal stalemates
        min_y_speed = 2.0
        if abs(y_speed) < min_y_speed:
            y_speed = min_y_speed if y_speed > 0 else -min_y_speed
            
        # Add small random variation to prevent predictable patterns
        y_speed += random.uniform(-0.5, 0.5)
        
        # Ensure speed doesn't exceed maximum
        max_speed = 20
        current_speed = math.sqrt(x_speed * x_speed + y_speed * y_speed)
        if current_speed > max_speed:
            speed_multiplier = max_speed / current_speed
            x_speed *= speed_multiplier
            y_speed *= speed_multiplier


# -------------------- OPPONENT AI --------------------
def move_opponent():
    global opponent_paddle_speed

    if boss_mode:
        # Boss mode AI - Enhanced prediction and faster movement
        prediction_factor = 0.95  # Higher prediction accuracy
        max_speed = BOSS_PADDLE_SPEED
        
        # Predict where the ball will intersect with the opponent's y-position
        if x_speed < 0:  # Ball is moving towards opponent
            # Calculate time until ball reaches opponent's x position
            time_to_intercept = (opponent.centerx - ball.centerx) / -x_speed
            # Predict ball's y position at intercept
            predicted_y = ball.centery + (y_speed * time_to_intercept * prediction_factor)
            
            # Account for bounces
            while predicted_y < 0 or predicted_y > HEIGHT:
                if predicted_y < 0:
                    predicted_y = -predicted_y
                if predicted_y > HEIGHT:
                    predicted_y = 2 * HEIGHT - predicted_y
        else:
            # If ball is moving away, return to center with some randomization
            predicted_y = HEIGHT / 2 + random.randint(-50, 50)

        # Move towards the predicted position
        if opponent.centery < predicted_y - 5:
            opponent_paddle_speed = min(opponent_paddle_speed + PADDLE_ACCELERATION * 2, max_speed)
        elif opponent.centery > predicted_y + 5:
            opponent_paddle_speed = max(opponent_paddle_speed - PADDLE_ACCELERATION * 2, -max_speed)
        else:
            opponent_paddle_speed = 0
    else:
        # Simple AI for normal mode - directly follow the ball
        speed = MAX_PADDLE_SPEED * ai_difficulty  # Use AI difficulty to scale the speed
        
        # Simple up/down movement based on ball position
        if opponent.centery < ball.centery:
            opponent.y += speed
        elif opponent.centery > ball.centery:
            opponent.y -= speed

    # Keep paddle in bounds
    if opponent.top < 0:
        opponent.top = 0
    if opponent.bottom > HEIGHT:
        opponent.bottom = HEIGHT

# -------------------- MAIN GAME LOOP --------------------
show_start_menu()
reset_ball()

while True:
    keys_pressed = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
                if paused:
                    pygame.mixer.music.pause()
                    show_pause_menu()
                else:
                    pygame.mixer.music.unpause()

    if not paused:
        handle_ball_movement()
        handle_paddle_movement()
        move_opponent()


    draw_screen()
    pygame.display.update()
    CLOCK.tick(60)
