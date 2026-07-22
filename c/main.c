#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

static const int LINES[8][3] = {{0,1,2},{3,4,5},{6,7,8},{0,3,6},{1,4,7},{2,5,8},{0,4,8},{2,4,6}};
static long nodes = 0;

char winner(const char board[10]) {
    for (int i = 0; i < 8; ++i) {
        int a = LINES[i][0], b = LINES[i][1], c = LINES[i][2];
        if (board[a] != '-' && board[a] == board[b] && board[b] == board[c]) return board[a];
    }
    return 0;
}

int has_empty(const char board[10]) {
    return strchr(board, '-') != NULL;
}

int minimax(char board[10], char current, char ai, int depth, int alpha, int beta) {
    nodes++;
    char win = winner(board);
    if (win == ai) return 10 - depth;
    if (win != 0) return depth - 10;
    if (!has_empty(board)) return 0;

    int maximizing = current == ai;
    int best = maximizing ? -100 : 100;
    for (int i = 0; i < 9; ++i) {
        if (board[i] != '-') continue;
        board[i] = current;
        int score = minimax(board, current == 'X' ? 'O' : 'X', ai, depth + 1, alpha, beta);
        board[i] = '-';
        if (maximizing) {
            if (score > best) best = score;
            if (best > alpha) alpha = best;
        } else {
            if (score < best) best = score;
            if (best < beta) beta = best;
        }
        if (beta <= alpha) break;
    }
    return best;
}

int main(int argc, char **argv) {
    const char *input = argc > 1 ? argv[1] : "XX-OO----";
    char ai = argc > 2 ? (char)toupper((unsigned char)argv[2][0]) : 'X';
    if (strlen(input) != 9 || (ai != 'X' && ai != 'O')) {
        fprintf(stderr, "error: board must have 9 cells and player must be X or O\n");
        return 2;
    }

    char board[10];
    for (int i = 0; i < 9; ++i) {
        board[i] = (char)toupper((unsigned char)input[i]);
        if (board[i] != 'X' && board[i] != 'O' && board[i] != '-') {
            fprintf(stderr, "error: board may contain only X, O, -\n");
            return 2;
        }
    }
    board[9] = '\0';
    if (winner(board) || !has_empty(board)) {
        fprintf(stderr, "error: board must be a non-terminal position\n");
        return 2;
    }

    int best_move = -1, best_score = -100;
    nodes = 0;
    for (int i = 0; i < 9; ++i) {
        if (board[i] != '-') continue;
        board[i] = ai;
        int score = minimax(board, ai == 'X' ? 'O' : 'X', ai, 1, -100, 100);
        board[i] = '-';
        if (score > best_score) {
            best_score = score;
            best_move = i;
        }
    }
    printf("{\"language\":\"c\",\"move\":%d,\"score\":%d,\"nodes\":%ld}\n", best_move, best_score, nodes);
    return 0;
}
