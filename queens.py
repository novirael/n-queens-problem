#!/usr/bin/env/python3

import time
import sys
import csv
import argparse
import numpy as np


class CommonQueens(object):
    board = None
    deep = 0

    solutions = 0
    duration = 0
    max_deep = 0

    filename = None

    def _reset_stats(self):
        self.solutions = 0
        self.duration = 0
        self.max_deep = 0

    def resolve(self, n):
        self.board = [[0 for _ in range(n)] for _ in range(n)]
        self._reset_stats()
        start_time = time.time()
        self._go_for(0)
        self.duration = time.time() - start_time

    def _go_for(self, n):
        raise NotImplementedError()

    def _preview_board(self):
        for row in self.board:
            for column in row:
                print(str(column) + ' ', end="")
            print()
        print()

    def resolve_single_board(self, size):
        print("Looking for solutions on board with size %d." % size)
        self.resolve(size)
        print("Solutions", self.solutions)

    def resolve_multiple_boards(self, max_size):
        print("Preparing file", self.filename)
        with open(self.filename, 'w') as file:
            file_writer = csv.writer(file)
            file_writer.writerow([
                'board_size',
                'solutions',
                'duration',
                'max_deep',
            ])

            for size in range(1, max_size):
                self.resolve_single_board(size)

                file_writer.writerow([
                    size,
                    self.solutions,
                    self.duration,
                    self.max_deep,
                ])


class QueenBacktracking(CommonQueens):
    filename = 'queens-backtracking-sum.csv'

    def _go_for(self, row):
        self.deep += 1
        max_size = len(self.board)

        if row >= max_size:
            self.solutions += 1
            self.max_deep = max(self.deep, self.max_deep)
            self.deep = 0
        else:
            for column in range(max_size):
                if self._can_put_queen(row, column):
                    self.board[row][column] = 1
                    self._go_for(row + 1)
                    self.board[row][column] = 0

    def _can_put_queen(self, row, column):
        matrix = np.matrix(self.board)

        # y coordinate changes for matrix[::-1]
        new_row = range(len(self.board))[::-1][row]

        check = [
            matrix[row].any(),
            matrix[:, column].any(),
            matrix.diagonal(column - row).any(),
            matrix[::-1].diagonal(column - new_row).any()
        ]

        return not any(check)


class QueenForwardChecking(CommonQueens):
    filename = 'queens-forward-checking-sum.csv'

    def _go_for(self, row):
        self.deep += 1
        max_size = len(self.board)

        if row >= max_size:
            self._preview_board()
            self.solutions += 1
            self.max_deep = max(self.deep, self.max_deep)
            self.deep = 0
        else:
            if self._can_move(row):
                for column in range(max_size):
                    if self.board[row][column] == 0:
                        self.put_mark(row, column, row + 2)

                        if self._can_put_queen(row, column + 1):
                            self._go_for(row + 1)

                        self.put_mark(row, column, 0)

    def put_mark(self, y, x, value):
        max_size = len(self.board)
        matrix = np.matrix(self.board)

        # y coordinate changes for matrix[::-1]
        new_y = range(len(self.board))[::-1][y]

        matrix[:, x] = value
        matrix[y, :] = value
        i = abs(x - y)
        k = max_size
        matrix[-np.arange(k-i), np.arange(k-i) + i] = value

        i = abs(x - new_y)
        k = max_size
        matrix[::-1][np.arange(k-i)[:k] + i, np.arange(k-i)[:k]] = value

        self.board[y][x] = 'x' if value > 0 else '.'
        self._preview_board()

    def _can_move(self, row, true_on_end=False):
        max_size = len(self.board)
        if true_on_end and row >= max_size:
            return True
        return not any(self.board[row])

    def _can_put_queen(self, row, column):
        matrix = np.matrix(self.board)

        # y coordinate changes for matrix[::-1]
        new_row = range(len(self.board))[::-1][row]

        check = [
            matrix[row].any(),
            matrix[:, column].any(),
            matrix.diagonal(column - row).any(),
            matrix[::-1].diagonal(column - new_row).any()
        ]

        return not any(check)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('board_size', type=int, help='board size')
    parser.add_argument('--backtracking', action='store_true')
    parser.add_argument('--forward_checking', action='store_true')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.backtracking:
        print("Backtracking")
        instance = QueenBacktracking()
        instance.resolve_single_board(args.board_size)
        sys.exit()

    if args.forward_checking:
        print("Forward checking")
        instance = QueenForwardChecking()
        instance.resolve_single_board(args.board_size)
        sys.exit()

    print("All")
    for obj in (QueenBacktracking,):
        instance = obj()
        instance.resolve_multiple_boards(args.board_size)
