#!/usr/bin/env node
'use strict';

const WIN_LINES = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];

function winner(board) {
  for (const [a,b,c] of WIN_LINES) {
    if (board[a] !== '-' && board[a] === board[b] && board[b] === board[c]) return board[a];
  }
  return null;
}

function minimax(board, current, ai, depth, alpha, beta, stats) {
  stats.nodes += 1;
  const win = winner(board);
  if (win === ai) return 10 - depth;
  if (win !== null) return depth - 10;
  if (!board.includes('-')) return 0;

  const maximizing = current === ai;
  let best = maximizing ? -100 : 100;
  for (let i = 0; i < board.length; i += 1) {
    if (board[i] !== '-') continue;
    board[i] = current;
    const score = minimax(board, current === 'X' ? 'O' : 'X', ai, depth + 1, alpha, beta, stats);
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

function solve(boardText, player) {
  const board = boardText.toUpperCase().split('');
  const ai = player.toUpperCase();
  if (board.length !== 9 || board.some((c) => !'XO-'.includes(c))) throw new Error('board must contain exactly 9 characters from X, O, -');
  if (!['X','O'].includes(ai)) throw new Error('player must be X or O');
  if (winner(board) || !board.includes('-')) throw new Error('board must be a non-terminal position');

  let bestMove = -1;
  let bestScore = -100;
  const stats = {nodes: 0};
  for (let i = 0; i < board.length; i += 1) {
    if (board[i] !== '-') continue;
    board[i] = ai;
    const score = minimax(board, ai === 'X' ? 'O' : 'X', ai, 1, -100, 100, stats);
    board[i] = '-';
    if (score > bestScore) {
      bestScore = score;
      bestMove = i;
    }
  }
  return {language: 'javascript', move: bestMove, score: bestScore, nodes: stats.nodes};
}

try {
  const board = process.argv[2] || 'XX-OO----';
  const player = process.argv[3] || 'X';
  process.stdout.write(`${JSON.stringify(solve(board, player))}\n`);
} catch (error) {
  process.stderr.write(`error: ${error.message}\n`);
  process.exit(2);
}
