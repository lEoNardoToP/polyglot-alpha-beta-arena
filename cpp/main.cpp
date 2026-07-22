#include <algorithm>
#include <array>
#include <cctype>
#include <iostream>
#include <stdexcept>
#include <string>

constexpr std::array<std::array<int,3>,8> LINES{{{{0,1,2}},{{3,4,5}},{{6,7,8}},{{0,3,6}},{{1,4,7}},{{2,5,8}},{{0,4,8}},{{2,4,6}}}};
long long nodes = 0;

char winner(const std::string& board) {
    for (const auto& line : LINES) {
        const auto [a,b,c] = line;
        if (board[a] != '-' && board[a] == board[b] && board[b] == board[c]) return board[a];
    }
    return '\0';
}

int minimax(std::string& board, char current, char ai, int depth, int alpha, int beta) {
    ++nodes;
    const char win = winner(board);
    if (win == ai) return 10 - depth;
    if (win != '\0') return depth - 10;
    if (board.find('-') == std::string::npos) return 0;

    const bool maximizing = current == ai;
    int best = maximizing ? -100 : 100;
    for (int i = 0; i < 9; ++i) {
        if (board[i] != '-') continue;
        board[i] = current;
        const int score = minimax(board, current == 'X' ? 'O' : 'X', ai, depth + 1, alpha, beta);
        board[i] = '-';
        if (maximizing) {
            best = std::max(best, score);
            alpha = std::max(alpha, best);
        } else {
            best = std::min(best, score);
            beta = std::min(beta, best);
        }
        if (beta <= alpha) break;
    }
    return best;
}

int main(int argc, char** argv) {
    try {
        std::string board = argc > 1 ? argv[1] : "XX-OO----";
        char ai = argc > 2 ? static_cast<char>(std::toupper(argv[2][0])) : 'X';
        std::transform(board.begin(), board.end(), board.begin(), [](unsigned char c){ return static_cast<char>(std::toupper(c)); });
        if (board.size() != 9 || board.find_first_not_of("XO-") != std::string::npos) throw std::invalid_argument("invalid board");
        if (ai != 'X' && ai != 'O') throw std::invalid_argument("player must be X or O");
        if (winner(board) || board.find('-') == std::string::npos) throw std::invalid_argument("board must be non-terminal");

        int bestMove = -1, bestScore = -100;
        nodes = 0;
        for (int i = 0; i < 9; ++i) {
            if (board[i] != '-') continue;
            board[i] = ai;
            const int score = minimax(board, ai == 'X' ? 'O' : 'X', ai, 1, -100, 100);
            board[i] = '-';
            if (score > bestScore) { bestScore = score; bestMove = i; }
        }
        std::cout << "{\"language\":\"cpp\",\"move\":" << bestMove << ",\"score\":" << bestScore << ",\"nodes\":" << nodes << "}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
