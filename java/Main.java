import java.util.Locale;

public final class Main {
    private static final int[][] LINES = {{0,1,2},{3,4,5},{6,7,8},{0,3,6},{1,4,7},{2,5,8},{0,4,8},{2,4,6}};
    private static long nodes;

    private static char winner(char[] board) {
        for (int[] line : LINES) {
            int a = line[0], b = line[1], c = line[2];
            if (board[a] != '-' && board[a] == board[b] && board[b] == board[c]) return board[a];
        }
        return '\0';
    }

    private static boolean hasEmpty(char[] board) {
        for (char cell : board) if (cell == '-') return true;
        return false;
    }

    private static int minimax(char[] board, char current, char ai, int depth, int alpha, int beta) {
        nodes++;
        char win = winner(board);
        if (win == ai) return 10 - depth;
        if (win != '\0') return depth - 10;
        if (!hasEmpty(board)) return 0;

        boolean maximizing = current == ai;
        int best = maximizing ? -100 : 100;
        for (int i = 0; i < board.length; i++) {
            if (board[i] != '-') continue;
            board[i] = current;
            int score = minimax(board, current == 'X' ? 'O' : 'X', ai, depth + 1, alpha, beta);
            board[i] = '-';
            if (maximizing) {
                best = Math.max(best, score);
                alpha = Math.max(alpha, best);
            } else {
                best = Math.min(best, score);
                beta = Math.min(beta, best);
            }
            if (beta <= alpha) break;
        }
        return best;
    }

    public static void main(String[] args) {
        try {
            String boardText = (args.length > 0 ? args[0] : "XX-OO----").toUpperCase(Locale.ROOT);
            char ai = (args.length > 1 ? args[1] : "X").toUpperCase(Locale.ROOT).charAt(0);
            if (boardText.length() != 9 || !boardText.matches("[XO-]{9}")) throw new IllegalArgumentException("invalid board");
            if (ai != 'X' && ai != 'O') throw new IllegalArgumentException("player must be X or O");
            char[] board = boardText.toCharArray();
            if (winner(board) != '\0' || !hasEmpty(board)) throw new IllegalArgumentException("board must be non-terminal");

            int bestMove = -1, bestScore = -100;
            nodes = 0;
            for (int i = 0; i < board.length; i++) {
                if (board[i] != '-') continue;
                board[i] = ai;
                int score = minimax(board, ai == 'X' ? 'O' : 'X', ai, 1, -100, 100);
                board[i] = '-';
                if (score > bestScore) { bestScore = score; bestMove = i; }
            }
            System.out.printf("{\"language\":\"java\",\"move\":%d,\"score\":%d,\"nodes\":%d}%n", bestMove, bestScore, nodes);
        } catch (IllegalArgumentException error) {
            System.err.println("error: " + error.getMessage());
            System.exit(2);
        }
    }
}
