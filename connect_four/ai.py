import random

from .models import GameCF

# rand_table = [[3**(j*7 + i)
#                for j in range(7)] for i in range(6)]
rand_table = [[(random.randint(0, 2**31), random.randint(0, 2**31))
               for j in range(7)] for i in range(6)]
# table = [None] * (2**16)
table = dict()


class BaseAI(GameCF):
    column_row = [5]*7

    class Meta:
        proxy = True

    def play(self, col: int) -> bool:
        if super().current_player().username != 'ai':
            b = super().play(col)
            if b:
                self.column_row[col] -= 1
        self.player_num = self.player
        self.state = super(GameCF, self).field()
        self.state_hash = self.hash(self.state)
        for column in range(self.WIDTH):
            row = self.HEIGHT
            for i in range(self.HEIGHT):
                if self.state[i][column] is not None:
                    row = i
                    break
            self.column_row[column] = row-1
        if self.game_over:
            return True
        else:
            row = self.column_row[col] + 1
            i, j = self.move()
            return i, j, row, col

    def get_available_moves(self):
        moves = list()
        for col in [3, 2, 4, 1, 5, 0, 6]:
            if 6 > self.column_row[col] >= 0:
                moves.append(col)
        return moves

    def hash(self, state: list) -> int:
        hash = 0
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                if state[i][j] is not None:
                    hash ^= rand_table[i][j][state[i][j]-1]
        return hash

    def make_move(self, col: int, player):
        row = self.column_row[col]
        self.state[row][col] = player
        self.state_hash ^= rand_table[row][col][player-1]
        self.column_row[col] -= 1

    def unmake_move(self, col: int):
        self.column_row[col] += 1
        row = self.column_row[col]
        player = self.state[row][col]
        self.state[row][col] = None
        self.state_hash ^= rand_table[row][col][player-1]

    def evaluate(self, depth: int, state=None):
        if state is None:
            state = self.state
        # horizontal check
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH - 3):
                if state[i][j+0] == state[i][j+1] == state[i][j+2] == state[i][j+3]:
                    if state[i][j] == self.player:
                        return depth * 100
                    elif state[i][j] is not None:
                        return -depth * 100

        # vertical check
        for i in range(self.HEIGHT - 3):
            for j in range(self.WIDTH):
                if state[i+0][j] == state[i+1][j] == state[i+2][j] == state[i+3][j]:
                    if state[i][j] == self.player:
                        return depth * 100
                    elif state[i][j] is not None:
                        return -depth * 100

        # diagonal 1 check
        for i in range(self.HEIGHT - 3):
            for j in range(self.WIDTH - 3):
                if state[i+0][j+0] == state[i+1][j+1] == state[i+2][j+2] == state[i+3][j+3]:
                    if state[i][j] == self.player:
                        return depth * 100
                    elif state[i][j] is not None:
                        return -depth * 100

        # diagonal 2 check
        for i in range(self.HEIGHT - 3):
            for j in range(3, self.WIDTH):
                if state[i+0][j-0] == state[i+1][j-1] == state[i+2][j-2] == state[i+3][j-3]:
                    if state[i][j] == self.player:
                        return depth * 100
                    elif state[i][j] is not None:
                        return -depth * 100
        return 0


class RandomCFAI(BaseAI):
    slug = 'random'

    class Meta:
        proxy = True

    def move(self):
        col = random.randint(0, self.WIDTH-1)
        while not super(BaseAI, self).play(col):
            col = random.randint(0, self.WIDTH-1)
        return self.column_row[col], col


class NegamaxTTTAI(BaseAI):
    slug = 'negamax'

    class Meta:
        proxy = True

    def move(self):
        col = self.negamax(self.player_num, 4)[0]
        super(BaseAI, self).play(col)
        return self.column_row[col], col

    def negamax(self, player: int, depth: int):
        colour = (2*player - 3) * (2*self.player_num - 3)
        moves = self.get_available_moves()
        score = self.evaluate(depth)
        if not moves or score or not depth:
            return (-1, colour * score)
        best_move = moves[0]
        best_score = float('-inf')
        for col in moves:
            self.make_move(col, player)
            score = -self.negamax(3-player, depth-1)[1]
            self.unmake_move(col)
            if score > best_score:
                best_move = col
                best_score = score

        return best_move, best_score


class NegamaxPruningTTTAI(BaseAI):
    slug = 'negamax-pruning'

    class Meta:
        proxy = True

    def move(self):
        col = self.negamax(self.player, 8, float('-inf'), float('inf'))[0]
        super(BaseAI, self).play(col)
        return self.column_row[col], col

    def negamax(self, player: int, depth: int, alpha: int, beta: int):
        colour = (2*player - 3) * (2*self.player_num - 3)
        moves = self.get_available_moves()
        score = self.evaluate(depth)
        if not moves or score or not depth:
            return (-1, colour * score)
        best_move = moves[0]
        best_score = float('-inf')
        for col in moves:
            self.make_move(col, player)
            score = -self.negamax(3-player, depth-1, -beta, -alpha)[1]
            self.unmake_move(col)
            if score > best_score:
                best_move = col
                best_score = score
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
            # if depth > 4:
            #     print('\t'*(6-depth)+f'move: ({col}), score: {score}')
        return best_move, best_score


class PrincipalVariationSearchAI(BaseAI):
    slug = 'pvs'

    class Meta:
        proxy = True

    def move(self):
        col = self.pvs(self.player_num, 10, float('-inf'), float('inf'))[0]
        super(BaseAI, self).play(col)
        return self.column_row[col], col

    def pvs(self, player: int, depth: int, alpha: int, beta: int):
        colour = (2*player - 3) * (2*self.player_num - 3)
        moves = self.get_available_moves()
        score = self.evaluate(depth)
        if not moves or score or not depth:
            return (-1, colour * score)
        best_move = moves[0]
        best_score = float('-inf')
        for col in moves:
            self.make_move(col, player)
            if col == moves[0]:
                score = -self.pvs(3-player, depth-1, -beta, -alpha)[1]
            else:
                score = -self.pvs(3-player, depth-1, -alpha-1, -alpha)[1]
                if alpha < score < beta and depth > 2:
                    score = -self.pvs(3-player, depth-1, -beta, -alpha)[1]
            self.unmake_move(col)
            if score > best_score:
                best_move = col
                best_score = score
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
            # if depth > 4:
            #     print('\t'*(6-depth)+f'move: ({col}), score: {score}')
        return best_move, best_score


class NegamaxABTablesAI(BaseAI):
    slug = 'negamax-tables'

    class Meta:
        proxy = True

    def move(self):
        for i in range(6, 13, 2):
            col, val = self.negamax(self.player_num, i, float('-inf'), float('inf'))
            print(f'depth {i} done, MEM: {len(table)}')
        super(BaseAI, self).play(col)
        return self.column_row[col], col

    class TT:

        def __init__(self, lb=None, ub=None, d=None):
            self.lbound = lb
            self.ubound = ub
            self.depth = d

    def tt_lookup(self, state_hash: int):
        return table.get(state_hash, self.TT())
        # return table[state_hash] or self.TT()

    def tt_store(self, state_hash: int, tt_entry: TT):
        table[state_hash] = tt_entry

    def negamax(self, player: int, depth: int, alpha: int, beta: int):
        colour = (2*player - 3) * (2*self.player_num - 3)
        alpha_orig = alpha
        tt_entry: self.TT = self.tt_lookup(self.state_hash)
        if (tt_entry.lbound is not None or tt_entry.ubound is not None) and tt_entry.depth >= depth:
            if tt_entry.lbound == tt_entry.ubound:
                return (tt_entry.move, tt_entry.lbound)
            if tt_entry.lbound is not None:
                if tt_entry.lbound >= beta:
                    return (tt_entry.move, tt_entry.lbound)
                alpha = max(alpha, tt_entry.lbound)
            if tt_entry.ubound is not None:
                if tt_entry.ubound <= alpha:
                    return (tt_entry.move, tt_entry.ubound)
                beta = min(beta, tt_entry.ubound)
            if alpha >= beta:
                if tt_entry.lbound is not None:
                    return (tt_entry.move, tt_entry.lbound)
                else:
                    return (tt_entry.move, tt_entry.ubound)
        moves = self.get_available_moves()
        score = self.evaluate(depth)
        if not moves or score or not depth:
            return (-1, colour * score)
        best_move = moves[0]
        best_score = float('-inf')
        for col in moves:
            self.make_move(col, player)
            score = -self.negamax(3-player, depth-1, -beta, -alpha)[1]
            self.unmake_move(col)
            # if depth > 8:
            #     print('\t'*(10-depth) + f'col {col} ({score})')
            if score > best_score:
                best_move = col
                best_score = score
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        tt_entry.move = best_move
        tt_entry.depth = depth
        if best_score <= alpha_orig:
            # tt_entry.flag = 'UPPERBOUND'
            tt_entry.ubound = best_score
        elif best_score >= beta:
            # tt_entry.flag = 'LOWERBOUND'
            tt_entry.lbound = best_score
        else:
            # tt_entry.flag = 'EXACT'
            tt_entry.ubound = best_score
            tt_entry.lbound = best_score

        self.tt_store(self.state_hash, tt_entry)
        return best_move, best_score


class MTDFAI(NegamaxABTablesAI):
    slug = 'mtd-f'

    class Meta:
        proxy = True

    def move(self):
        val = 0
        for i in range(6, 13, 2):
            val, col = self.MTD(val, i)
            print(f'depth {i} done, MEM: {len(table)}')
        super(BaseAI, self).play(col)
        return self.column_row[col], col

    def MTD(self, f, depth):
        g = f
        upperbound = float('+inf')
        lowerbound = float('-inf')
        move = -1
        while lowerbound < upperbound:
            beta = max(g, lowerbound+1)
            move, g = self.negamax(self.player_num, depth, beta-1, beta)
            if g < beta:
                upperbound = g
            else:
                lowerbound = g
        return move, g


class BNSAI(NegamaxABTablesAI):
    slug = 'bns'

    class Meta:
        proxy = True

    def get_available_moves(self):
        moves = list()
        for col in reversed([3, 2, 4, 1, 5, 0, 6]):
            if self.column_row[col] >= 0:
                moves.append(col)
        return moves

    def move(self):
        col = self.BNS(12, -12, 12)
        super(BaseAI, self).play(col)
        return self.column_row[col], col

    def BNS(self, depth, alpha: int, beta: int):
        moves = self.get_available_moves()
        subtree_count = len(moves)
        if moves:
            best_move = moves[0]
        while subtree_count != 1:
            test = self.next_guess(alpha, beta, subtree_count)
            better_count = 0
            for col in moves:
                self.make_move(col, self.player_num)
                score = -self.negamax(3-self.player_num, depth, -test, -test+1)[1]
                self.unmake_move(col)
                # print(f'move: ({col}), score: {score}')
                if score >= test:
                    best_move = col
                    better_count += 1
            if better_count != 0:
                subtree_count = better_count
                alpha = test
            else:
                beta = test
            if beta - alpha < 2:
                break
        return best_move

    def next_guess(self, alpha, beta, subtree_count):
        return alpha + (beta - alpha) * (subtree_count - 1) // (subtree_count)
