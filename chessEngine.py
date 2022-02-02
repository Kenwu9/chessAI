'''
The main engine. Handles movement of pieces.
'''
class GameState():

    def __init__(self):
        #Creating an 8 by 8 2D list, representing an 8 by 8 chessboard.
        #The items in the list are pieces and blanks on the board.
        #items beginning with 'b' are black pieces
        #items beginning with 'w' are white pieces
        # self.board = [
        #     ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
        #     ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        #     ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]]
 
        self.board = [
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "br", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "wp", "--", "--"],
            ["--", "--", "--", "--", "--", "wn", "--", "--"],
            ["--", "--", "wp", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"]]

        self.move_functions = {'p' : self.get_pawn_moves, 'r' : self.get_rook_moves, 'n' : self.get_knight_moves, 'b' : self.get_bishop_moves,
                              'k' : self.get_king_moves, 'q' : self.get_queen_moves}

        self.white_to_move = True
        self.moveLog = []
   
        # keeping track of king locations
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)

        #if the game ends in check_mate or stale_mate
        self.check_mate = False
        self.stale_mate = False
        self.enpassant_possible = () #stores the square for which enpassant is possible
        self.current_castling_right = Castle_rights(True, True, True, True) #start off with all castling options available
        self.castle_rights_log = [Castle_rights(self.current_castling_right.wks, self.current_castling_right.bks,
                                                self.current_castling_right.wqs, self.current_castling_right.bqs)] #first object


    #This function does not work for en passant, casting, or pawn promotion. This just executes regular moves
    def make_move(self, move):
        #move is already valid when we move it, because the user is only allowed to make valid moves. Illegal moves are not options
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved
        self.moveLog.append(move) #stores the move in the log for future usage
        self.white_to_move = not self.white_to_move #switch turns between white and black
        #update king location
        if move.piece_moved == 'wk':
            self.white_king_location = (move.end_row, move.end_column)
        elif move.piece_moved == 'bk':
            self.black_king_location = (move.end_row, move.end_column)
        #pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + 'q' #gets the color of the pawn moved and make it a queen
        #en passant
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_column] = '--' #to capture the pawn behind
        #update possible enpassant moves
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2: #if opponent moves pawn two squares
            self.enpassant_possible = ((move.start_row + move.end_row)//2, move.start_column)
        else:
            self.enpassant_possible = ()
            '''
            anytime a pawn move is made with the engine, enpassant_possible will be modified. If a non-pawn piece is moved, enpassant_possible will be reset
            '''
        #castle
        if move.is_castle_move:
            if move.end_column - move.start_column == 2: #king side castle
                self.board[move.end_row][move.end_column-1] = self.board[move.end_row][move.end_column+1] #move rook from old to new position
                self.board[move.end_row][move.end_column+1] = '--' #remove the old rook
            else: #queen side castle
                self.board[move.end_row][move.end_column+1] = self.board[move.end_row][move.end_column-2] #move rook from old to new position
                self.board[move.end_row][move.end_column-2] = '--' #remove the old rook

        #update castling rights if a rook or king moves
        self.update_castle_rights(move)
        self.castle_rights_log.append(Castle_rights(self.current_castling_right.wks, self.current_castling_right.bks,
                                                self.current_castling_right.wqs, self.current_castling_right.bqs))


    #undoes the move
    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.white_to_move = not self.white_to_move
            #update king location
        if move.piece_moved == 'wk':
            self.white_king_location = (move.start_row, move.start_column)
        elif move.piece_moved == 'bk':
            self.black_king_location = (move.start_row, move.start_column)


        #undo the enpassant move
        if move.is_enpassant_move:
            self.board[move.end_row][move.end_column] = '--' #empties the square of the first move
            self.board[move.start_row][move.end_column] = move.piece_captured
            self.enpassant_possible = (move.end_row, move.end_column) #ensures that enpassant is still possible after undoing the move
        
        #undo pawn 2 square move
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ()
        #undoing castling rights
        self.castle_rights_log.pop() #remove new castle rights
        new_rights = self.castle_rights_log[-1]
        #assign last castle right to current castle right
        self.current_castling_right = Castle_rights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)
        
        #undoing castling moves
        if move.is_castle_move:
            if move.end_column - move.start_column == 2: #if king side
                self.board[move.end_row][move.end_column+1] = self.board[move.end_row][move.end_column-1]
                self.board[move.end_row][move.end_column-1] = '--'
            else: #if queen side
                self.board[move.end_row][move.end_column-2] = self.board[move.end_row][move.end_column+1]
                self.board[move.end_row][move.end_column+1] = '--'

        self.check_mate = False
        self.stale_mate = False
            

    '''
    update the castle rights
    '''
    def update_castle_rights(self, move):
        if move.piece_moved == 'wk': #if white king is moved
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved == 'bk': #if black king is moved
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.piece_moved == 'wr': #if white rook is moved
            if move.start_row == 7:
                if move.start_column == 0: #meaning this is left rook
                    self.current_castling_right.wqs = False
                elif move.start_column ==7: #meaning this is right rook
                    self.current_castling_right.wks = False                 
        elif move.piece_moved == 'br': #if black rook is moved
            if move.start_row == 0:
                if move.start_column == 0: #meaning this is left rook
                    self.current_castling_right.bqs = False
                elif move.start_column == 7: #meaning this is right rook
                    self.current_castling_right.bks = False


    #all moves considering checks (if a piece is pinned, then it cannot be moved)
    def get_valid_moves(self):
        #creating a copy of the enpassant move so that the value of enpassant_possible can be modified
        temp_enpassant = self.enpassant_possible
        #creating a copy of castle_rights
        temp_castle_rights = Castle_rights(self.current_castling_right.wks, self.current_castling_right.bks,
                                           self.current_castling_right.wqs, self.current_castling_right.bqs)
        # first generate all possible moves
        moves = self.get_all_possible_moves()
        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        # next, make the move
        for i in range(len(moves)-1, -1, -1): #iterating through the list of moves backwards
            self.make_move(moves[i])
            
            # after move made, generate opponent moves and check for attacks on the king
            self.white_to_move = not self.white_to_move #switch the turn back to white
            if self.in_check():
                moves.remove(moves[i]) # if found, then the move is not valid
            self.white_to_move = not self.white_to_move    
            self.undo_move() #to cancel out the make_move operation
        
        if len(moves) == 0: #if there is no valid moves, then the game has ended
            if self.in_check(): #if the king is currently in check, then it is checkmate
                self.check_mate = True
            else: #if not, it is stalemate
                self.stale_mate = True

        self.enpassant_possible = temp_enpassant
        self.current_castling_right = temp_castle_rights
        return moves


    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move #switch turns
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move #switch back turn order
        for move in opp_moves:
            if move.end_row == r and move.end_column == c: #check whether square is under attack
                #if one of them is under attack
                return True
        #if none
        return False
        
   #get all possible moves
    def get_all_possible_moves(self):
        moves = []

        #go through the board by row by column
        for r in range(len(self.board)):
            for c in range (len(self.board[r])):
                turn = self.board[r][c][0] #get the first character of the name of the piece on the grid to see if it is white or black
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves) #gets and calls the function from dictionary for the corresponding piece
        return moves
   
    #get all possible pawn moves at that location and add to list
    def get_pawn_moves(self, r, c, moves):
        #FOR WHITE
        if self.white_to_move:
            if self.board[r-1][c] == "--": #if the square in front of it is empty
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #if the second square in front it is ALSO empty
                    moves.append(Move((r, c), (r-2, c), self.board))    
            #Pawn capture options to the left and right
            #ensure the piece does not capture off the board
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b': #if there is a black piece that can be captured
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassant_possible: #if the square that the pawn is going to is a possible enpassant move
                    moves.append(Move((r, c), (r-1, c-1), self.board, is_enpassant_move=True))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassant_possible: #if the square that the pawn is going to is a possible enpassant move
                    moves.append(Move((r, c), (r-1, c+1), self.board, is_enpassant_move=True))
    #FOR BLACK
        elif not self.white_to_move:

            if self.board[r+1][c] == "--": #if the square in front of it is empty
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": #if the second square in front it is ALSO empty
                    moves.append(Move((r, c), (r+2, c), self.board))
        #Pawn capture options to the left and right
        #ensure the piece does not capture off the board
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w': #if there is a white piece that can be captured
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassant_possible: #if the square that the pawn is going to is a possible enpassant move
                    moves.append(Move((r, c), (r+1, c-1), self.board, is_enpassant_move=True))  
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassant_possible: #if the square that the pawn is going to is a possible enpassant move
                    moves.append(Move((r, c), (r+1, c+1), self.board, is_enpassant_move=True))  

    def get_rook_moves(self, r, c, moves):
        #FOR WHITE
        if self.white_to_move:
            #possible horizontal moves - to the right
            for d in range(7-c):
                if self.board[r][c+1+d] == "--":
                    moves.append(Move((r, c), (r, c+1+d), self.board))
                elif self.board[r][c+1+d][0] == 'b': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r, c+1+d), self.board))
                    break
                else: #can only be white piece if code reaches here
                    break       
            #possible horizontal moves - to the left
            for d in range(c):
                if self.board[r][c-1-d] == "--":
                    moves.append(Move((r, c), (r, c-1-d), self.board))              
                elif self.board[r][c-1-d][0] == 'b': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r, c-1-d), self.board))
                    break
                else:
                    break         
            #possible vertical moves - to the top
            for d in range(r):
                if self.board[r-1-d][c] == "--":
                    moves.append(Move((r, c), (r-1-d, c), self.board))   
                elif self.board[r-1-d][c][0] == 'b': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r-1-d, c), self.board))
                    break
                else:
                    break
            #possible vertical moves - to the bottom
            for d in range(7-r):
                if self.board[r+1+d][c] == "--":
                    moves.append(Move((r, c), (r+1+d, c), self.board))
                elif self.board[r+1+d][c][0] == 'b': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r+1+d, c), self.board))
                    break
                else: #can only be white piece if code reaches here
                    break
        #FOR BLACK
        else:
            #possible horizontal moves - to the right
            for d in range(7-c):
                if self.board[r][c+1+d] == "--":
                    moves.append(Move((r, c), (r, c+1+d), self.board))
                elif self.board[r][c+1+d][0] == 'w': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r, c+1+d), self.board))
                    break
                else: #can only be white piece if code reaches here
                    break
            
            #possible horizontal moves - to the left
            for d in range(c):
                if self.board[r][c-1-d] == "--":
                    moves.append(Move((r, c), (r, c-1-d), self.board))              
                elif self.board[r][c-1-d][0] == 'w': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r, c-1-d), self.board))
                    break
                else:
                    break
            
            #possible vertical moves - to the top
            for d in range(r):
                if self.board[r-1-d][c] == "--":
                    moves.append(Move((r, c), (r-1-d, c), self.board))   
                elif self.board[r-1-d][c][0] == 'w': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r-1-d, c), self.board))
                    break
                else:
                    break

            #possible vertical moves - to the bottom
            for d in range(7-r):
                if self.board[r+1+d][c] == "--":
                    moves.append(Move((r, c), (r+1+d, c), self.board))
                elif self.board[r+1+d][c][0] == 'w': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r+1+d, c), self.board))
                    break
                else: #can only be white piece if code reaches here
                    break

    def get_knight_moves(self, r, c, moves):
        # #FOR WHITE
        # if self.white_to_move:
        #     if r-1 >= 0 and c-2 >= 0:
        #         if self.board[r-1][c-2] == "--" or self.board[r-1][c-2][0] == "b":
        #             moves.append(Move((r, c), (r-1, c-2), self.board))
        #     if r-2 >= 0 and  c-1 >= 0:
        #         if self.board[r-2][c-1] == "--" or self.board[r-2][c-1][0] == "b":
        #             moves.append(Move((r, c), (r-2, c-1), self.board))
        #     if r-2 >= 0 and c+1 <= 7:
        #         if self.board[r-2][c+1] == "--" or self.board[r-2][c+1][0] == "b":
        #             moves.append(Move((r, c), (r-2, c+1), self.board))
        #     if r-1 >= 0 and c+2 <= 7:
        #         if self.board[r-1][c+2] == "--" or self.board[r-1][c+2][0] == "b":
        #             moves.append(Move((r, c), (r-1, c+2), self.board))
        #     if r+1 <= 7 and c+2 <= 7:
        #         if self.board[r+1][c+2] == "--" or self.board[r+1][c+2][0] == "b":
        #             moves.append(Move((r, c), (r+1, c+2), self.board))
        #     if r+2 <= 7 and c+1 <= 7:
        #         if self.board[r+2][c+1] == "--" or self.board[r+2][c+1][0] == "b":
        #             moves.append(Move((r, c), (r+2, c+1), self.board))
        # #FOR BLACK
        # if not self.white_to_move:
        #     if r-1 >= 0 and c-2 >= 0:
        #         if self.board[r-1][c-2] == "--" or self.board[r-1][c-2][0] == "w":
        #             moves.append(Move((r, c), (r-1, c-2), self.board))
        #     if r-2 >= 0 and  c-1 >= 0:
        #         if self.board[r-2][c-1] == "--" or self.board[r-2][c-1][0] == "w":
        #             moves.append(Move((r, c), (r-2, c-1), self.board))
        #     if r-2 >= 0 and c+1 <= 7:
        #         if self.board[r-2][c+1] == "--" or self.board[r-2][c+1][0] == "w":
        #             moves.append(Move((r, c), (r-2, c+1), self.board))
        #     if r-1 >= 0 and c+2 <= 7:
        #         if self.board[r-1][c+2] == "--" or self.board[r-1][c+2][0] == "w":
        #             moves.append(Move((r, c), (r-1, c+2), self.board))
        #     if r+1 <= 7 and c+2 <= 7:
        #         if self.board[r+1][c+2] == "--" or self.board[r+1][c+2][0] == "w":
        #             moves.append(Move((r, c), (r+1, c+2), self.board))
        #     if r+2 <= 7 and c+1 <= 7:
        #         if self.board[r+2][c+1] == "--" or self.board[r+2][c+1][0] == "w":
        #             moves.append(Move((r, c), (r+2, c+1), self.board))



        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.white_to_move else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_column = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_piece = self.board[end_row][end_column]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_column), self.board))


    def get_bishop_moves(self, r, c, moves):
        #FOR WHITE
        if self.white_to_move:
            #top-right diagonal
            for d in range(7-c):
                if r-1-d < 0:
                    break
                if c+1+d > 7:
                    break
                if self.board[r-1-d][c+1+d] == "--":
                    moves.append(Move((r, c), (r-1-d, c+1+d), self.board))
                elif self.board[r-1-d][c+1+d][0] == 'b': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r-1-d, c+1+d), self.board))
                    break
                else: #can only be white piece if code reaches here
                    break
            #top-left diagonal
            for d in range(c):
                if r-1-d < 0:
                    break
                if c-1-d < 0:
                    break
                if self.board[r-1-d][c-1-d] == "--":
                    moves.append(Move((r, c), (r-1-d, c-1-d), self.board))              
                elif self.board[r-1-d][c-1-d][0] == 'b': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r-1-d, c-1-d), self.board))
                    break
                else:
                    break      
            #bottom-right diagonal
            for d in range(7-r):
                if r+1+d > 7:
                    break
                if c+1+d > 7:
                    break
                if self.board[r+1+d][c+1+d] == "--":
                    moves.append(Move((r, c), (r+1+d, c+1+d), self.board))   
                elif self.board[r+1+d][c+1+d][0] == 'b': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r+1+d, c+1+d), self.board))
                    break
                else:
                    break
            #bottom-left diagonal
            for d in range(7-r):
                if r+1+d > 7:
                    break
                if c-1-d < 0:
                    break
                if self.board[r+1+d][c-1-d] == "--":
                    moves.append(Move((r, c), (r+1+d, c-1-d), self.board))
                elif self.board[r+1+d][c-1-d][0] == 'b': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r+1+d, c-1-d), self.board))
                    break
                else: #can only be white piece if code reaches here
                    break         
        #FOR BLACK
        if not self.white_to_move:
            #top-right diagonal
            for d in range(7-c):
                if r-1-d < 0:
                    break
                if c+1+d > 7:
                    break
                if self.board[r-1-d][c+1+d] == "--":
                    moves.append(Move((r, c), (r-1-d, c+1+d), self.board))
                elif self.board[r-1-d][c+1+d][0] == 'w': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r-1-d, c+1+d), self.board))
                    break
                else: #can only be white piece if code reaches here
                    break      
            #top-left diagonal
            for d in range(c):
                if r-1-d < 0:
                    break
                if c-1-d < 0:
                    break
                if self.board[r-1-d][c-1-d] == "--":
                    moves.append(Move((r, c), (r-1-d, c-1-d), self.board))              
                elif self.board[r-1-d][c-1-d][0] == 'w': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r-1-d, c-1-d), self.board))
                    break
                else:
                    break 
            #bottom-right diagonal
            for d in range(7-r):
                if r+1+d > 7:
                    break
                if c+1+d > 7:
                    break
                if self.board[r+1+d][c+1+d] == "--":
                    moves.append(Move((r, c), (r+1+d, c+1+d), self.board))   
                elif self.board[r+1+d][c+1+d][0] == 'w': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r+1+d, c+1+d), self.board))
                    break
                else:
                    break
            #bottom-left diagonal
            for d in range(7-r):
                if r+1+d > 7:
                    break
                if c-1-d < 0:
                    break
                if self.board[r+1+d][c-1-d] == "--":
                    moves.append(Move((r, c), (r+1+d, c-1-d), self.board))
                elif self.board[r+1+d][c-1-d][0] == 'w': #if the square contains an opponent's piece
                    moves.append(Move((r, c), (r+1+d, c-1-d), self.board))
                    break
                else: #can only be white piece if code reaches here
                    break

    def get_king_moves(self, r, c, moves):

        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))
    
        #self.get_castle_moves(r, c, moves, ally_color)

    '''
    using some helper functions to simplify castling mechanics
    '''
    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c): #used in_check() function before, but gives infinite recursion, so switched to square_under_attack() function
            return #if king is in check
        if (self.white_to_move and self.current_castling_right.wks) or (not self.white_to_move and self.current_castling_right.bks):
            self.get_ks_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castling_right.wqs) or (not self.white_to_move and self.current_castling_right.bqs):
            self.get_qs_castle_moves(r, c, moves)
    def get_ks_castle_moves(self, r, c, moves): #king side castle moves
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True))
    def get_qs_castle_moves(self, r, c, moves): #queen side castle moves
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3]:
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)


class Castle_rights():
    def __init__(self, wks, bks, wqs, bqs):
        #keeping track of castling rights
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    #map keys to values
    #key : value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}

    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7,}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_column = start_sq[1]
        self.end_row = end_sq[0]
        self.end_column = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]
        #pawn promotion
        self.is_pawn_promotion = False #flags whether there is a pawn promotion move
        if (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7):
            self.is_pawn_promotion = True #record a pawn promotion move once it reaches the edge of the board
        #en passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp' #manually telling the engine that a pawn has been captured
        #castle move
        self.is_castle_move = is_castle_move
        #move ID
        self.move_id = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column #assigning a unique ID to each move
    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        #this converts position to proper chess notation so that it can be stored and analyzed
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column) 

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]