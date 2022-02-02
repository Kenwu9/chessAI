# AI CHESS ENGINE, by KEN WU

#### Video Demo: https://www.youtube.com/watch?v=GqyVCjIernA

#### Description:

This is an AI chess engine that uses the MinMax algorithm to find the next best move to play. The project consists of three files: chessMain.py, chessEngine.py, and chessAI.py. chessMain.py contains the "main" function which draws the chess board and deals with user inputs. chessEngine.py is responsible for the majority of move mechanics and board graphics/game states. chessAI.py contains the MinMax algorithm. 

I chose to implement the Min Max algorithm instead of the greedy algorithm. When I implemented the greedy algorithm, I realized that the AI would simply look one move ahead and choose the move that grants it the most material points. This is a naive algorithm because it doesn't take into account the possible retaliatory moves the opponent can make. For example, in the case where the AI can take a pawn with its queen, it will do so, without checking whether the opponent can take its queen the next move. The Min Max algorithm, on the other hand, evaluates not only the best possible move for its current board position but also tries to minimize the opponent's best move. For instance, if move A grants the AI +1 point but allows the opponent to make a +5 move while move B grants the AI 0 point yet limits the opponent's best move to only 1 point, it will choose move B over move A, because move B minimizes the opponent's score while simultaneously maximizing its own score.