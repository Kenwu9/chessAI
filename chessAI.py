'''
Handles the AI aspect of the program.
'''

import random

piece_score = {'k': 0, 'q': 10, 'r': 5, 'b': 3, 'n': 3, 'p': 1} #assigning a value for every piece on the board
CHECKMATE = 1000
STALEMATE = 0

'''
the goal of the AI for white is to try to make black score as low as possible, and vice versa for black AI
'''

def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]

#currently only looking 2 moves ahead
def find_best_move(gs, valid_moves):
    turn_multiplier = 1 if gs.white_to_move else -1 #triggers player turn exchange
    opponent_min_max_score = CHECKMATE #this is the worst possible score for black
    best_player_move = None
    random.shuffle(valid_moves) #so that the AI doesn't repeat the same move over and over
    #black will try to bring this score down
    for player_move in valid_moves:
        gs.make_move(player_move)
        opponents_moves = gs.get_valid_moves()
        if gs.stale_mate:
            opponent_max_score = STALEMATE
        elif gs.check_mate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE #check opponent's best move when responding to the AI's move
            for opponents_move in opponents_moves:
                gs.make_move(opponents_move)
                gs.get_valid_moves()
                if gs.check_mate:
                    score = CHECKMATE
                elif gs.stale_mate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_material(gs.board) #pass in the board state and return a score based on the current game state
                if (score > opponent_max_score):
                    opponent_max_score = score #find a move that lowers the score for black. That move will be the best move
                gs.undo_move()
        #score minimization part
        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        gs.undo_move()
    return best_player_move

'''
score the board based on material
'''

def score_material(board):
    score = 0
    for row in board:
        for square in row:
            #score based on piece
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]
    return score