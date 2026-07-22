<?php
declare(strict_types=1);

const LINES = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
$nodes = 0;

function winner(array $board): ?string {
    foreach (LINES as [$a, $b, $c]) {
        if ($board[$a] !== '-' && $board[$a] === $board[$b] && $board[$b] === $board[$c]) return $board[$a];
    }
    return null;
}

function minimax(array &$board, string $current, string $ai, int $depth, int $alpha, int $beta): int {
    global $nodes;
    $nodes++;
    $win = winner($board);
    if ($win === $ai) return 10 - $depth;
    if ($win !== null) return $depth - 10;
    if (!in_array('-', $board, true)) return 0;

    $maximizing = $current === $ai;
    $best = $maximizing ? -100 : 100;
    foreach ($board as $i => $cell) {
        if ($cell !== '-') continue;
        $board[$i] = $current;
        $score = minimax($board, $current === 'X' ? 'O' : 'X', $ai, $depth + 1, $alpha, $beta);
        $board[$i] = '-';
        if ($maximizing) {
            $best = max($best, $score);
            $alpha = max($alpha, $best);
        } else {
            $best = min($best, $score);
            $beta = min($beta, $best);
        }
        if ($beta <= $alpha) break;
    }
    return $best;
}

try {
    $boardText = strtoupper($argv[1] ?? 'XX-OO----');
    $ai = strtoupper($argv[2] ?? 'X');
    if (strlen($boardText) !== 9 || preg_match('/^[XO-]{9}$/', $boardText) !== 1) throw new InvalidArgumentException('invalid board');
    if (!in_array($ai, ['X','O'], true)) throw new InvalidArgumentException('player must be X or O');
    $board = str_split($boardText);
    if (winner($board) !== null || !in_array('-', $board, true)) throw new InvalidArgumentException('board must be non-terminal');

    $bestMove = -1;
    $bestScore = -100;
    $nodes = 0;
    foreach ($board as $i => $cell) {
        if ($cell !== '-') continue;
        $board[$i] = $ai;
        $score = minimax($board, $ai === 'X' ? 'O' : 'X', $ai, 1, -100, 100);
        $board[$i] = '-';
        if ($score > $bestScore) { $bestScore = $score; $bestMove = $i; }
    }
    echo json_encode(['language' => 'php', 'move' => $bestMove, 'score' => $bestScore, 'nodes' => $nodes], JSON_UNESCAPED_SLASHES) . PHP_EOL;
} catch (InvalidArgumentException $error) {
    fwrite(STDERR, 'error: ' . $error->getMessage() . PHP_EOL);
    exit(2);
}
