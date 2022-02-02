'''
MIN MAX CHESS by KEN WU
'''

"""
The main driver file. Responsible for handling user input and displaying the current GameState.
"""
import pygame as p
import chessEngine, chessAI

WIDTH = HEIGHT = 512
DIMENSION = 8 #dimensions of board
SQ_SIZE = HEIGHT // DIMENSION
IMAGES = {} #of pieces

"""
Load in the images.
Initialize a global dictionary of images. Only called once in the main.
"""

def load_images():
    pieces = ['wp', 'wr', 'wb', 'wn', 'wk', 'wq',
            'bp', 'br', 'bb', 'bn', 'bk', 'bq']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #now we can access every image through the IMAGES dictionary

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = chessEngine.GameState()
    valid_moves = gs.get_valid_moves() #we can only make the moves in the valid_moves list
    move_made = False #flag variable for when a move is made
    load_images()
    running = True
    sq_selected = () #storing location of the square selected as a tuple. Emply because no square is selected initially. Tuple: (row, col)
    player_clicks = [] #keeps track of player clicks (two tuples)
    game_over = False
    player1 = True #if human plays white, then True. If AI plays white, then False
    player2 = False #same for black


    while running:
        human_turn = (gs.white_to_move and player1) or (not gs.white_to_move and player2)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #below handles mouse actions
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn: #only allowed to move pieces if the game is not over and human player is playing
                    location = p.mouse.get_pos() #keeps track of x and y location of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    
                    if sq_selected == (row, col): #checks whether the user clicks the same square twice
                        sq_selected = () #deselects the square
                        player_clicks = [] #clears player clicks
                    
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected) #append for both 1st and 2nd clicks
                    
                    if len(player_clicks) == 2: #checks whether it is the second click
                        move = chessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        #make the move only if it is valid
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                sq_selected = () #this resets user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected] #this fixes the bug that occurs when user selects a piece when another has already been selected.

            #below handles key actions
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #if the key Z is pressed, call undo_move() function
                    gs.undo_move()
                    move_made = True #if a move is undone, generate a new set of valid moves, because undoing a move will change the set of valid moves.
                    game_over = False #if game is over, then undoing a move should undo the 'game over' too.
                if e.key == p.K_r: #reset the board
                    gs = chessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    game_over = False
        
        #Chess AI
        if not game_over and not human_turn:
            AI_move = chessAI.find_best_move(gs, valid_moves)
            if AI_move is None: #if the engine sees it has lost the game, then it should generate random moves
                AI_move = chessAI.find_random_move(valid_moves)
            gs.make_move(AI_move)
            move_made = True

        #if a move is made, set flag to false again, and generate a new set of valid moves.
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_gamestate(screen, gs, valid_moves, sq_selected)
        if gs.check_mate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, 'Black Wins By Checkmate!')
            else:
                draw_text(screen, 'White Wins By Checkmate!')
        elif gs.stale_mate:
            game_over = True
            draw_text(screen, 'Stalemate!')

        p.display.flip()


'''
Highlight squares
'''
def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'): #if the square selected is a valid piece that can be moved
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparent value. 0 = transparent, 255 = opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_column == c:
                    screen.blit(s, (move.end_column*SQ_SIZE, move.end_row*SQ_SIZE))


'''
Responsible for drawing graphics within current game state
'''
def draw_gamestate(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)

def draw_board(screen):
    colors = [p.Color('tan4'), p.Color('burlywood1')]
    for x in range(DIMENSION):
        for y in range(DIMENSION):
            color = colors[((x+y)%2)]
            p.draw.rect(screen, color, p.Rect(y*SQ_SIZE, x*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    for x in range(DIMENSION):
        for y in range(DIMENSION):
            piece = board[y][x]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(x*SQ_SIZE, y*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_text(screen, text):
    font = p.font.SysFont('Helvitca', 40, True, False)
    text_object = font.render(text, 0, p.Color('Gray'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))

if __name__ == "__main__":
    main()
