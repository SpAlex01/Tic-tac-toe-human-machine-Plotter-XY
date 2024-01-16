import random


class Tic(object):
    winningCombos = (
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6])

    winners = ('X-win', 'Draw', 'O-win')

    def __init__(self, squares=[]):
        if len(squares) == 0:
            self.squares = [None for i in range(9)]
        else:
            self.squares = squares

    def evaluate(self, node, player):
        if node.xWon():
            return -1
        elif node.oWon():
            return 1
        else:
            return 0

    def show(self):
        for element in [self.squares[i:i + 3] for i in range(0, len(self.squares), 3)]:
            print(element)
        print("\r\n")

    def availableMoves(self):
        return [k for k, v in enumerate(self.squares) if v is None]

    def complete(self):
        if None not in [v for v in self.squares]:
            return True
        if self.winner() is not None:
            return True
        return False

    def xWon(self):
        return self.winner() == 'X'

    def oWon(self):
        return self.winner() == 'O'

    def tied(self):
        return self.complete() and self.winner() is None

    def winner(self):
        for player in ('X', 'O'):
            positions = self.getSquares(player)
            for combo in self.winningCombos:
                win = True
                for pos in combo:
                    if pos not in positions:
                        win = False
                if win:
                    return player
        return None

    def getSquares(self, player):
        return [k for k, v in enumerate(self.squares) if v == player]

    def makeMove(self, position, player):
        self.squares[position] = player

    def alphabeta(self, node, player, alpha, beta, depth):
        if node.complete() or depth == 0:
            return self.evaluate(node, player)

        for move in node.availableMoves():
            node.makeMove(move, player)
            val = -self.alphabeta(node, getEnemy(player), -beta, -alpha, depth - 1)
            node.makeMove(move, None)

            if val > alpha:
                alpha = val
                if alpha >= beta:
                    break

        return alpha


def determine(board, player, depth=3):
    a = -float('inf')
    choices = []

    for move in board.availableMoves():
        board.makeMove(move, player)
        val = -board.alphabeta(board, getEnemy(player), -float('inf'), float('inf'), depth - 1)
        board.makeMove(move, None)

        if val > a:
            a = val
            choices = [move]
        elif val == a:
            choices.append(move)

    return random.choice(choices)


def getEnemy(player):
    if player == 'X':
        return 'O'
    return 'X'


# Example usage:
if __name__ == '__main__':
    board = Tic()
    player = 'X'

    while not board.complete():
        if player == 'X':
            move = determine(board, player, depth=3)
        else:
            move = int(input(f"Enter your move (0-8) as {player}: "))

        if move in board.availableMoves():
            board.makeMove(move, player)
            board.show()
            player = getEnemy(player)
        else:
            print("Invalid move. Try again.")

    if board.xWon():
        print("X wins!")
    elif board.oWon():
        print("O wins!")
    else:
        print("It's a draw!")
