from random import shuffle
import sys
import pygame as pg

# Define constants
FPS = 30
WIDTH = 550  # Window width
HEIGHT = 550  # Window height
CARD_SIZE = 75
GAPSIZE = 10  # Size of gap between cards
GRIDSIZE = 6  # Size of square grid
MARGIN = 25

# Defines colors to be used for background, card backs, and shapes
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)

BG_COLOR = CYAN
CARD_COLOR = WHITE

# Define the shapes to use
SQUARE = 'square'
TRIANGLE = 'triangle'
DIAMOND = 'diamond'
CIRCLE = 'circle'
LINE = 'line'
DONUT = 'donut'

# Having tuples of all the shapes and their colors will be helpful
COLORS = (RED, GREEN, BLUE)
SHAPES = (SQUARE, TRIANGLE, DIAMOND, CIRCLE, LINE, DONUT)


# Some design notes I made on the needed functions

# create_game_board
# board will be a list containing 6 lists, each of these 6 lists represnting a column
# the items in the 6 lists will be tuples (shape, color)
# will return board list

# create_revealed_cards (list for tracking which cards have been revealed)
# the list will contain 6 lists each representing a column of the board.
# Each item in each column will be initialized to False
# will return revealed list

# get_card_coords(column, row) - will get reference coordinates for cards to help with drawing
# cards and shapes as well as determining selected cards. The column and row parameters refer
# to the indices of the card in the board object
# will return tuple

# draw_board(board, revealed, screen)   will use board and revealed to determine what to draw
# Will draw all unrevealed cards, and will call draw_shapes for each revealed card
# draw_shapes(board, column, row, screen)

# get_shape_and_color(board, column, row)  will get the shape and color of a card
# this will be used when drawing shapes and also when checking matches
# will return a tuple containing the shape and color of the card indicated by (column, row)

# get_selected_card (mouse position)
# will return a tuple (column, row) indicating the cards positions in board

# check_match (card1, card2)
# will return True if card1 and card2 have the same shape and color, False otherwise

# check_win(revealed) - win if revealed values are all True
# Will return True if all of the values in the revealed array are True, False otherwise


def create_game_board():
    '''Create a game board'''
    # Create a list containing two of each shape/color combination
    colored_shapes = []
    for color in COLORS:
        for shape in SHAPES:
            colored_shapes.append((shape, color))
            colored_shapes.append((shape, color))
    shuffle(colored_shapes)

    # Create the board
    board = []
    for x in range(GRIDSIZE):
        # Create a list for each column
        column = []
        for y in range(GRIDSIZE):
            # Append the first colored_shape and remove it from the list
            column.append(colored_shapes[0])
            del colored_shapes[0]
        board.append(column)
    return board


def create_revealed_cards():
    '''Creates an array to track which cards are revealed'''
    revealed = []
    for x in range(GRIDSIZE):
        # Create a list for each column
        column = []
        for y in range(GRIDSIZE):
            # No cards are revealed initially
            column.append(False)
        revealed.append(column)
    return revealed


def get_card_coords(column, row):
    '''Return coordinates of the top left corner of a card'''
    left = MARGIN + column * (CARD_SIZE + GAPSIZE)
    top = MARGIN + row * (CARD_SIZE + GAPSIZE)
    return (left, top)


def draw_board(board, revealed, screen):
    '''Draw the game board'''
    for column in range(GRIDSIZE):
        for row in range(GRIDSIZE):
            left, top = get_card_coords(column, row)
            # For any unrevealed card, draw a card sized rectangle
            if not revealed[column][row]:
                pg.draw.rect(screen, CARD_COLOR,
                             (left, top, CARD_SIZE, CARD_SIZE))
            # Otherwise draw the colored shape for that card
            else:
                draw_shape(board, column, row, screen)


def draw_shape(board, column, row, screen):
    '''Draw the shape located at (column, row)'''
    shape, color = get_shape_and_color(board, column, row)
    left, top = get_card_coords(column, row)

    # Shape offsets from card coordinates
    half = int(CARD_SIZE * 0.5)
    quarter = int(CARD_SIZE * 0.25)

    if shape == SQUARE:
        pg.draw.rect(screen, color, (left + quarter, top +
                                     quarter, CARD_SIZE - half, CARD_SIZE - half))
    elif shape == TRIANGLE:
        pg.draw.polygon(screen, color, ((left + half, top + quarter),
                                        (left + quarter,  top +
                                         CARD_SIZE - quarter),
                                        (left + CARD_SIZE - quarter, top + CARD_SIZE - quarter)))
    elif shape == DIAMOND:
        pg.draw.polygon(screen, color, ((left + half, top + quarter), (left + quarter, top + half),
                                        (left + half, top + CARD_SIZE - quarter), (left + CARD_SIZE - quarter, top + half)))
    elif shape == CIRCLE:
        pg.draw.circle(screen, color, (left + half, top + half), quarter)
    elif shape == LINE:
        pg.draw.line(screen, color, (left + quarter, top + half),
                     (left + CARD_SIZE - quarter, top + half), quarter)
    elif shape == DONUT:
        pg.draw.circle(screen, color, (left + half, top + half), quarter)
        pg.draw.circle(screen, BG_COLOR,
                       (left + half, top + half), quarter // 2)


def get_shape_and_color(board, column, row):
    '''Return a tuple containing the shape and color located at (column, row)'''
    return board[column][row]


def get_selected_card(mouse_x, mouse_y):
    '''Return the column, row position of the selected card'''
    for column in range(GRIDSIZE):
        for row in range(GRIDSIZE):
            left, top = get_card_coords(column, row)
            card_Rect = pg.Rect(left, top, CARD_SIZE, CARD_SIZE)
            if card_Rect.collidepoint(mouse_x, mouse_y):
                return (column, row)
    return (None, None)


def check_match(board, card1, card2):
    '''Determine whether two cards match'''
    shape1, color1 = get_shape_and_color(board, card1[0], card1[1])
    shape2, color2 = get_shape_and_color(board, card2[0], card2[1])
    if shape1 == shape2 and color1 == color2:
        return True
    else:
        return False


def check_win(revealed):
    '''Checks to see if the player has won'''
    for column in revealed:
        if False in column:
            return False
    return True


def main():
    pg.init()

    # Initialize clock for setting FPS
    clock = pg.time.Clock()

    # Initialize main window
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption('Memory')

    # Initialize variables to store mouse click coordinates
    mouse_x = 0
    mouse_y = 0

    # Initialize variable to store first selection each round
    first_card = None

    # Create a game board
    board = create_game_board()

    # Initialize variable to track revealed cards
    revealed = create_revealed_cards()

    # Create a variable to keep track of the game state
    card_selected = False

    # Start the main game loop
    while True:

        # Draw/redraw everything
        screen.fill(BG_COLOR)
        draw_board(board, revealed, screen)

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos

        card = get_selected_card(mouse_x, mouse_y)

        # If no unrevealed card was selected do nothing
        if None in card or revealed[card[0]][card[1]]:
            pass

        # If selected card is the first selected this round, store its value and reveal it
        elif card_selected == False:
            first_card = card
            revealed[card[0]][card[1]] = True
            # Note that a first card has been selected for the current round
            card_selected = True

        # If selected card is the second selected this round, reveal it
        elif card_selected == True:
            revealed[card[0]][card[1]] = True

            # Redraw everything and wait before checking for match (so that the second shape is
            # displayed before being flipped back over if no match)
            screen.fill(BG_COLOR)
            draw_board(board, revealed, screen)
            pg.display.update()
            pg.time.wait(750)

            # If there's a match, reset card_selected and first_card
            if check_match(board, first_card, card):
                card_selected = False
                first_card = None
                # If the game is over, reset and start a new game
                if check_win(revealed):
                    pg.time.wait(2000)

                    # Reset the board
                    board = create_game_board()
                    revealed = create_revealed_cards()
                    mouse_x = 0
                    mouse_y = 0

            # If there isn't a match flip the cards back over and move to next round
            else:
                revealed[first_card[0]][first_card[1]] = False
                revealed[card[0]][card[1]] = False
                card_selected = False
                first_card = None
                mouse_x = 0
                mouse_y = 0

        pg.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
