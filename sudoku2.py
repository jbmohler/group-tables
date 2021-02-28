import copy
import random


class Impossible(BaseException):
    pass


class GroupConfig:
    def __init__(self, size):
        self._size = size
        self.rSize = list(range(self.size()))

        self.completed = None

        self.permbands = []
        for i in self.rSize:
            self.permbands.append(tuple(self.index((i, y)) for y in self.rSize))
            self.permbands.append(tuple(self.index((x, i)) for x in self.rSize))

        self.membership = [None] * (self.size() ** 2)
        for i in range(self.size() ** 2):
            self.membership[i] = tuple(g for g in self.permbands if i in g)

    def size(self):
        return self._size

    def index(self, coord):
        if type(coord) is tuple:
            return coord[0] * self.size() + coord[1]
        else:
            return coord

    def coordinates(self, coord):
        if type(coord) is tuple:
            return coord[0], coord[1]
        else:
            return coord / self.size(), coord % self.size()

    def __repr__(self):
        return "Group permbands for a %ix%i grid." % (self.size(), self.size())

    def fix_point(self, board, coord, n):
        idx = self.index(coord)
        if not type(board[idx]) is list:
            if n != board[idx]:
                raise Impossible

        board[idx] = n

        for mem in self.membership[idx]:
            for i in mem:
                if i != idx:
                    self.remove_choice(board, i, n)

    def remove_choice(self, board, coord, n):
        idx = self.index(coord)
        if (type(board[idx]) is list) and (n in board[idx]):
            board[idx].remove(n)
            if len(board[idx]) == 1:
                self.fix_point(board, idx, board[idx][0])
        elif (not type(board[idx]) is list) and n == board[idx]:
            raise Impossible

    def good_index_min_choices(self, board):
        min_list_size = self.size()
        min_cell = None
        for idx in range(self.size() ** 2):
            if type(board[idx]) is list:
                if len(board[idx]) < min_list_size:
                    min_list_size = len(board[idx])
                    min_cell = idx

        return min_cell

    def good_index_min_group(self, board):
        # pass
        weights = []
        for g in self.permbands:
            weights.append(
                (g, sum([len(board[idx]) for idx in g if type(board[idx]) is list]))
            )
        weights.sort(key=lambda x: x[1])
        grp = None
        for i in range(len(weights)):
            if weights[i][1] > 0:
                grp = weights[i][0]
                break

        if grp is None:
            return None
        else:
            min_list_size = self.size()
            min_cell = None
            for idx in grp:
                if type(board[idx]) is list:
                    if len(board[idx]) < min_list_size:
                        min_list_size = len(board[idx])
                        min_cell = idx

            return min_cell

    good_index = good_index_min_choices

    def solve(self, board):
        idx = self.good_index(board)
        if idx is None:
            self.completed(board)
        elif len(board[idx]) == 0:
            raise Impossible
        else:
            for n in board[idx]:
                next_board = copy.deepcopy(board)
                try:
                    # print "Set %i to %i" % (idx,n)
                    self.fix_point(next_board, idx, n)
                    # sb=GroupBoard(size=self.size())
                    # sb.board = next_board
                    # print sb
                    self.solve(next_board)
                    #self.completed()
                except Impossible:
                    continue
            # raise Impossible


class GroupBoard:
    def __init__(self, size, alphabet):
        self.config = GroupConfig(size)
        self.alphabet = alphabet
        self.board = [
            list(alphabet) for j in self.config.rSize for k in self.config.rSize
        ]

    def __repr__(self):
        s = self.config.size()
        rows = []
        for i in self.config.rSize:
            cells = []
            for j in self.config.rSize:
                if type(self.board[self.config.index((i, j))]) is list:
                    cells.append(
                        "".join(map(str, self.board[self.config.index((i, j))]))
                    )
                else:
                    cells.append(str(self.board[self.config.index((i, j))]))
            rows.append(" ".join(map(lambda x: "%-*s" % (s, x), cells)))
        return "\n".join(rows)

    def size(self):
        return self.config.size()

    def fix_grid(self, content):
        assert type(content) is list
        assert len(content) == self.size()

        for i in self.config.rSize:
            if content[i] != None:
                assert type(content[i]) is list
                self.fix_row(i, content[i])

    def fix_row(self, row, content):
        assert type(content) is list
        assert len(content) == self.size()

        for i in self.config.rSize:
            if content[i] != 0 and content[i] != None:
                self.fix_point((row, i), content[i])

    def fix_point(self, coord, n):
        self.config.fix_point(self.board, coord, n)

    def shuffle(self):
        s = self.size()
        for b in self.board:
            if type(b) is list:
                random.shuffle(b)

    def solve(self):
        newb = self.config.solve(self.board)
        if newb is None:
            return None
        else:
            sb = GroupBoard(size=self.size(), alphabet=self.alphabet)
            sb.board = newb
            return sb

    def __getitem__(self, coords):
        return self.board[self.config.index(coords)]

    def group_op(self, e1, e2):
        i1 = self.alphabet.index(e1)
        i2 = self.alphabet.index(e2)

        return self[(i1, i2)]

    def left_order(self, e1):
        current = e1
        result = 1
        while current != self.alphabet[0]:
            current = self.group_op(current, e1)
            result += 1
        return result


    def right_order(self, e1):
        current = e1
        result = 1
        while current != self.alphabet[0]:
            current = self.group_op(e1, current)
            result += 1
        return result


def group_identity(size, alphabet, identity):
    s2 = GroupBoard(size, alphabet)

    _alpha = list(alphabet)
    for i in s2.config.rSize:
        e = _alpha[i]
        s2.fix_point((i, 0), e)
        s2.fix_point((0, i), e)
    return s2


def Group_FromFile(file):
    lines = open(file, "r").readlines()
    lines = [l.strip() for l in lines if l != ""]
    s2 = GroupBoard(size=len(lines))

    def cell(c):
        if c == "*":
            return 0
        else:
            return int(c)

    for i in range(len(lines)):
        s2.fix_row(i, [cell(c) for c in lines[i]])

    return s2
