import copy
import random
import pygame

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game variables
cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
one_deck = 4 * cards
decks = 4
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h  # Full screen width and height
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
pygame.display.set_caption('Pygame Blackjack!')
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 30)
smaller_font = pygame.font.Font('freesansbold.ttf', 40)
active = False
records = [0, 0, 0]  # [wins, losses, draws]
player_score = 0
dealer_score = 0
initial_deal = False
my_hand = []
dealer_hand = []
outcome = 0
reveal_dealer = False
hand_active = False
add_score = False
results = ['', 'PLAYER BUSTED o_O', 'Player WINS! :)', 'DEALER WINS :(', 'TIE GAME...']

# Load casino table background
casino_table = pygame.image.load('assets/casino_table.png')
casino_table = pygame.transform.scale(casino_table, (WIDTH, HEIGHT))

# Load background music
pygame.mixer.music.load("assets/background_music.mp3")  # Replace with the path to your audio file
pygame.mixer.music.set_volume(0.1)  # Set the volume (optional)
pygame.mixer.music.play(-1, 0.0)  # Play the music indefinitely

# Load sounds
win_sound = pygame.mixer.Sound('assets/win_sound.wav')
lose_sound = pygame.mixer.Sound('assets/lose_sound.wav')
draw_sound = pygame.mixer.Sound('assets/draw_sound.wav')
final_win_sound = pygame.mixer.Sound('assets/finla_win_sound.wav')
final_lose_sound = pygame.mixer.Sound('assets/finla_lose_sound.wav')
final_win_sound = pygame.mixer.Sound('assets/final_win_sound.wav')
final_lose_sound = pygame.mixer.Sound('assets/final_lose_sound.wav')

# Functions
def deal_cards(current_hand, current_deck):
    card = random.randint(0, len(current_deck) - 1)
    current_hand.append(current_deck[card])
    current_deck.pop(card)
    return current_hand, current_deck


def draw_scores(player, dealer):
    screen.blit(font.render(f'Score[{player}]', True, 'white'), (350, 550))
    if reveal_dealer:
        screen.blit(font.render(f'Score[{dealer}]', True, 'white'), (350, 250))


def draw_cards(player, dealer, reveal):
    for i in range(len(player)):
        pygame.draw.rect(screen, 'white', [580 + (70 * i), 460 + (5 * i), 120, 220], 0, 5)
        screen.blit(font.render(player[i], True, 'black'), (585 + 70 * i, 465 + 5 * i))
        screen.blit(font.render(player[i], True, 'black'), (585 + 70 * i, 635 + 5 * i))
        pygame.draw.rect(screen, 'red', [580 + (70 * i), 460 + (5 * i), 120, 220], 5, 5)

    for i in range(len(dealer)):
        pygame.draw.rect(screen, 'white', [580 + (70 * i), 160 + (5 * i), 120, 220], 0, 5)
        if i != 0 or reveal:
            screen.blit(font.render(dealer[i], True, 'black'), (585 + 70 * i, 165 + 5 * i))
            screen.blit(font.render(dealer[i], True, 'black'), (585 + 70 * i, 335 + 5 * i))
        else:
            screen.blit(font.render('???', True, 'black'), (585 + 70 * i, 165 + 5 * i))
            screen.blit(font.render('???', True, 'black'), (585 + 70 * i, 335 + 5 * i))
        pygame.draw.rect(screen, 'blue', [580 + (70 * i), 160 + (5 * i), 120, 220], 5, 5)


def calculate_score(hand):
    hand_score = 0
    aces_count = hand.count('A')
    for card in hand:
        if card in cards[:8]:  # '2' to '9'
            hand_score += int(card)
        elif card in ['10', 'J', 'Q', 'K']:
            hand_score += 10
        elif card == 'A':
            hand_score += 11
    while hand_score > 21 and aces_count > 0:
        hand_score -= 10
        aces_count -= 1
    return hand_score


def draw_game(act, record, result):
    button_list = []
    if not act:
        deal = pygame.draw.rect(screen, 'white', [600, 200, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [600, 200, 300, 100], 3, 5)
        deal_text = font.render('DEAL HAND', True, 'black')
        screen.blit(deal_text, (650, 240))
        button_list.append(deal)
    else:
        hit = pygame.draw.rect(screen, 'white', [350, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [350, 700, 300, 100], 3, 5)
        hit_text = font.render('HIT ME', True, 'black')
        screen.blit(hit_text, (450, 735))
        button_list.append(hit)
        stand = pygame.draw.rect(screen, 'white', [700, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [700, 700, 300, 100], 3, 5)
        stand_text = font.render('STAND', True, 'black')
        screen.blit(stand_text, (800, 735))
        button_list.append(stand)
        score_text = smaller_font.render(f'Wins: {record[0]}   Losses: {record[1]}   Draws: {record[2]}', True, 'white')
        screen.blit(score_text, (11, 820))
    if result != 0:
        screen.blit(font.render(results[result], True, 'white'), (600, 50))
        deal = pygame.draw.rect(screen, 'white', [1000, 350, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [1000, 350, 300, 100], 3, 5)
        deal_text = font.render('NEW HAND', True, 'black')
        screen.blit(deal_text, (1080, 390))
        button_list.append(deal)
    return button_list


def check_endgame(hand_act, deal_score, play_score, result, totals, add):
    if not hand_act and deal_score >= 17:
        if play_score > 21:
            result = 1  # Player busts
        elif deal_score < play_score <= 21 or deal_score > 21:
            result = 2  # Player wins
        elif play_score < deal_score <= 21:
            result = 3  # Dealer wins
        else:
            result = 4  # Tie
        if add:
            if result in [1, 3]:
                totals[1] += 1
            elif result == 2:
                totals[0] += 1
            else:
                totals[2] += 1
            add = False
            # Play the appropriate sound based on the result
            if result == 1:  # Player loses
                lose_sound.play()
            elif result == 2:  # Player wins
                win_sound.play()
            elif result == 3:  # Dealer wins
                lose_sound.play()  # Play losing sound when the dealer wins
            elif result == 4:  # Tie
                draw_sound.play()
    return result, totals, add
    

def display_end_game_message():
    # Pause background music and other sounds
    pygame.mixer.music.pause()
    win_sound.stop()  # Stop any other sounds
    lose_sound.stop()
    draw_sound.stop()

    if records[0] == 5:
        end_game_message = font.render("You WON the game!", True, 'green')
        final_win_sound.play()  # Play the winning sound
        screen.fill('black')  # Clear the screen
        screen.blit(end_game_message, (WIDTH // 2 - end_game_message.get_width() // 2, HEIGHT // 2 - end_game_message.get_height() // 2))
        pygame.display.flip()

        # Increase the delay to 5000 milliseconds (5 seconds) to show the message longer only when the player wins
        pygame.time.wait(6500)  # Wait for 6 seconds before restarting the game

    elif records[1] == 5:
        end_game_message = font.render("You LOST the game!", True, 'red')
        final_lose_sound.play()  # Play the losing sound
        screen.fill('black')  # Clear the screen
        screen.blit(end_game_message, (WIDTH // 2 - end_game_message.get_width() // 2, HEIGHT // 2 - end_game_message.get_height() // 2))
        pygame.display.flip()

        # Add a 3-second delay for the losing screen
        pygame.time.wait(6200)  # Wait for 3 seconds before restarting the game

    # Resume background music after the pop-up
    pygame.mixer.music.unpause()


# Main game loop
run = True
while run:
    timer.tick(fps)
    screen.blit(casino_table, (0, 0))
    
    # Check for end game condition (5 wins or 5 losses)
    if records[0] == 5 or records[1] == 5:
        display_end_game_message()  # Show popup message
        # Reset the game state
        records = [0, 0, 0]  # Reset records
        my_hand = []  # Clear hands
        dealer_hand = []
        player_score = 0
        dealer_score = 0
        active = False  # Game is inactive until the next round
        initial_deal = False
        outcome = 0
        continue  # Start a new round
        
    if initial_deal:
        for i in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        initial_deal = False
    if active:
        player_score = calculate_score(my_hand)
        draw_cards(my_hand, dealer_hand, reveal_dealer)
        if reveal_dealer:
            dealer_score = calculate_score(dealer_hand)
            if dealer_score < 17:
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        draw_scores(player_score, dealer_score)
    buttons = draw_game(active, records, outcome)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP:
            if not active:
                if buttons[0].collidepoint(event.pos):
                    active = True
                    initial_deal = True
                    game_deck = copy.deepcopy(decks * one_deck)
                    random.shuffle(game_deck)
                    my_hand = []
                    dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    add_score = True
            else:
                if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    my_hand, game_deck = deal_cards(my_hand, game_deck)
                elif buttons[1].collidepoint(event.pos) and not reveal_dealer:
                    reveal_dealer = True
                    hand_active = False
                elif len(buttons) == 3:
                    if buttons[2].collidepoint(event.pos):
                        active = True
                        initial_deal = True
                        game_deck = copy.deepcopy(decks * one_deck)
                        random.shuffle(game_deck)
                        my_hand = []
                        dealer_hand = []
                        outcome = 0
                        hand_active = True
                        reveal_dealer = False
                        add_score = True
                        dealer_score = 0
                        player_score = 0
    if hand_active and player_score >= 21:
        hand_active = False
        reveal_dealer = True
    outcome, records, add_score = check_endgame(hand_active, dealer_score, player_score, outcome, records, add_score)
    pygame.display.flip()
pygame.quit()