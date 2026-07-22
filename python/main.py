#!/usr/bin/env python3
import json
import sys

WIN_LINES = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))


def winner(board: list[str]) -> str | None:
    for a, b, c in WIN_LINES:
        if board[a] != '-' and board[a] == board[b] == board[c]:
            return board[a]
    return None


def minimax(board: list[str], current: str, ai: str, depth: int, alpha: int, beta: int, nodes: list[int]) -> int:
    nodes[0] += 1
    win = winner(board)
    if win == ai:
        return 10 - depth
    if win is not None:
        return depth - 10
    if '-' not in board:
        return 0

    maximizing = current == ai
    best = -100 if maximizing else 100

    for i, cell in enumerate(board):
        if cell != '-':
            continue
        board[i] = current
        score = minimax(board, 'O' if current == 'X' else 'X', ai, depth + 1, alpha, beta, nodes)
        board[i] = '-'
        if maximizing:
            best = max(best, score)
            alpha = max(alpha, best)
        else:
            best = min(best, score)
            beta = min(beta, best)
        if beta <= alpha:
            break
    return best


def solve(board_text: str, ai: str) -> dict[str, int | str]:
    board = list(board_text.upper())
    if len(board) != 9 or any(c not in 'XO-' for c in board):
        raise ValueError('board must contain exactly 9 characters from X, O, -')
    ai = ai.upper()
    if ai not in {'X', 'O'}:
        raise ValueError('player must be X or O')
    if winner(board) or '-' not in board:
        raise ValueError('board must be a non-terminal position')

    best_move = -1
    best_score = -100
    nodes = [0]
    for i, cell in enumerate(board):
        if cell != '-':
            continue
        board[i] = ai
        score = minimax(board, 'O' if ai == 'X' else 'X', ai, 1, -100, 100, nodes)
        board[i] = '-'
        if score > best_score:
            best_score = score
            best_move = i

    return {'language': 'python', 'move': best_move, 'score': best_score, 'nodes': nodes[0]}


def main() -> int:
    board = sys.argv[1] if len(sys.argv) > 1 else 'XX-OO----'
    player = sys.argv[2] if len(sys.argv) > 2 else 'X'
    try:
        print(json.dumps(solve(board, player), separators=(',', ':')))
        return 0
    except ValueError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
