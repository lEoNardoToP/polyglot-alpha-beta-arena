using System;
using System.Linq;
using System.Text.Json;

internal static class Program
{
    private static readonly int[][] Lines =
    {
        new[] {0,1,2}, new[] {3,4,5}, new[] {6,7,8}, new[] {0,3,6},
        new[] {1,4,7}, new[] {2,5,8}, new[] {0,4,8}, new[] {2,4,6}
    };

    private static long _nodes;

    private static char? Winner(char[] board)
    {
        foreach (var line in Lines)
        {
            var (a, b, c) = (line[0], line[1], line[2]);
            if (board[a] != '-' && board[a] == board[b] && board[b] == board[c]) return board[a];
        }
        return null;
    }

    private static int Minimax(char[] board, char current, char ai, int depth, int alpha, int beta)
    {
        _nodes++;
        var win = Winner(board);
        if (win == ai) return 10 - depth;
        if (win is not null) return depth - 10;
        if (!board.Contains('-')) return 0;

        var maximizing = current == ai;
        var best = maximizing ? -100 : 100;
        for (var i = 0; i < board.Length; i++)
        {
            if (board[i] != '-') continue;
            board[i] = current;
            var score = Minimax(board, current == 'X' ? 'O' : 'X', ai, depth + 1, alpha, beta);
            board[i] = '-';
            if (maximizing)
            {
                best = Math.Max(best, score);
                alpha = Math.Max(alpha, best);
            }
            else
            {
                best = Math.Min(best, score);
                beta = Math.Min(beta, best);
            }
            if (beta <= alpha) break;
        }
        return best;
    }

    private static int Main(string[] args)
    {
        try
        {
            var boardText = (args.Length > 0 ? args[0] : "XX-OO----").ToUpperInvariant();
            var aiText = (args.Length > 1 ? args[1] : "X").ToUpperInvariant();
            if (boardText.Length != 9 || boardText.Any(c => c is not ('X' or 'O' or '-'))) throw new ArgumentException("invalid board");
            if (aiText is not ("X" or "O")) throw new ArgumentException("player must be X or O");
            var board = boardText.ToCharArray();
            var ai = aiText[0];
            if (Winner(board) is not null || !board.Contains('-')) throw new ArgumentException("board must be non-terminal");

            var bestMove = -1;
            var bestScore = -100;
            _nodes = 0;
            for (var i = 0; i < board.Length; i++)
            {
                if (board[i] != '-') continue;
                board[i] = ai;
                var score = Minimax(board, ai == 'X' ? 'O' : 'X', ai, 1, -100, 100);
                board[i] = '-';
                if (score > bestScore) { bestScore = score; bestMove = i; }
            }

            Console.WriteLine(JsonSerializer.Serialize(new { language = "csharp", move = bestMove, score = bestScore, nodes = _nodes }));
            return 0;
        }
        catch (ArgumentException error)
        {
            Console.Error.WriteLine($"error: {error.Message}");
            return 2;
        }
    }
}
