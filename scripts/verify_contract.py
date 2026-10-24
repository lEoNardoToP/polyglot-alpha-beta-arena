#!/usr/bin/env python3
"""Check each engine against a separate exhaustive, unpruned game oracle.

Use --languages to select explicit local coverage. The default requires all
eight engines; unavailable toolchains fail rather than silently skipping them.
"""
from __future__ import annotations

import argparse
import hashlib
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("python", "javascript", "c", "cpp", "java", "php", "csharp", "swift")
LINES = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))


def winner(board: str) -> str | None:
    return next((board[a] for a, b, c in LINES
                 if board[a] != "-" and board[a] == board[b] == board[c]), None)


@lru_cache(maxsize=None)
def value(board: str, turn: str, player: str) -> int:
    """Unpruned full-tree value, independent of any engine's alpha-beta logic.

    Remaining empty cells encode preference for fast wins and delayed losses.
    The caller converts this root-independent value to its depth-based score.
    """
    won = winner(board)
    if won:
        return (10 + board.count("-")) * (1 if won == player else -1)
    moves = [i for i, cell in enumerate(board) if cell == "-"]
    if not moves:
        return 0
    scores = [value(board[:i] + turn + board[i + 1:],
                    "O" if turn == "X" else "X", player) for i in moves]
    return max(scores) if turn == player else min(scores)


def oracle(board: str, player: str) -> tuple[int, int]:
    candidates = [(value(board[:i] + player + board[i + 1:],
                         "O" if player == "X" else "X", player), i)
                  for i, cell in enumerate(board) if cell == "-"]
    # Equal-valued moves choose the lowest cell index, like the public contract.
    best, move = max(candidates, key=lambda item: (item[0], -item[1]))
    score = (1 if best > 0 else -1) * (abs(best) - board.count("-")) if best else 0
    return move, score


def reachable() -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    pending = [("---------", "X")]
    result = []
    while pending:
        board, turn = pending.pop()
        if (board, turn) in seen:
            continue
        seen.add((board, turn))
        if winner(board) or "-" not in board:
            continue
        result.append((board, turn))
        pending.extend((board[:i] + turn + board[i + 1:], "O" if turn == "X" else "X")
                       for i, cell in enumerate(board) if cell == "-")
    return sorted(result)


def run(argv: list[str], timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                          timeout=timeout, check=False)


def engines(languages: list[str], build: Path) -> dict[str, list[str]]:
    commands = {}
    for language in languages:
        tool = {"python": sys.executable, "javascript": "node", "c": "cc",
                "cpp": "c++", "java": "javac", "php": "php",
                "csharp": "dotnet", "swift": "swiftc"}[language]
        if not shutil.which(tool):
            raise RuntimeError(f"{language}: missing {tool}; select local coverage explicitly with --languages")
        compilation = None
        if language == "python":
            commands[language] = [sys.executable, str(ROOT / "python/main.py")]
        elif language == "javascript":
            commands[language] = ["node", str(ROOT / "javascript/main.js")]
        elif language in ("c", "cpp", "swift"):
            filename = {"c": "main.c", "cpp": "main.cpp", "swift": "main.swift"}[language]
            executable = str(build / language)
            flags = {"c": ["-std=c17", "-Wall", "-Wextra", "-pedantic", "-O2"],
                     "cpp": ["-std=c++20", "-Wall", "-Wextra", "-pedantic", "-O2"],
                     "swift": ["-O", "-module-cache-path", str(build / "swift-module-cache")]}[language]
            compilation = [tool, *flags, str(ROOT / language / filename), "-o", executable]
            commands[language] = [executable]
        elif language == "java":
            if not shutil.which("java"):
                raise RuntimeError("java: missing runtime")
            destination = build / "java"
            destination.mkdir()
            compilation = ["javac", "-d", str(destination), str(ROOT / "java/Main.java")]
            commands[language] = ["java", "-cp", str(destination), "Main"]
        elif language == "php":
            commands[language] = ["php", str(ROOT / "php/main.php")]
        elif language == "csharp":
            destination = build / "csharp"
            compilation = ["dotnet", "build", str(ROOT / "csharp/PolyglotAlphaBeta.csproj"),
                           "--configuration", "Release", "--output", str(destination), "--nologo"]
            commands[language] = ["dotnet", str(destination / "PolyglotAlphaBeta.dll")]
        if compilation:
            completed = run(compilation, 120)
            if completed.returncode:
                raise RuntimeError(f"{language}: build failed: {completed.stderr[-2000:]}")
    return commands


def verify(commands: dict[str, list[str]], cases: list[tuple[str, str]]) -> dict:
    invalid = [("short", "X"), ("---------x", "X"), ("!--------", "X"),
               ("---------", "Z"), ("XXXOO----", "O"), ("XOXOOXXXO", "X")]
    coverage = {}
    for language, argv in commands.items():
        for board, player in cases:
            completed = run([*argv, board, player])
            if completed.returncode:
                raise RuntimeError(f"{language}: valid input {board}/{player} failed: {completed.stderr[:300]}")
            output = json.loads(completed.stdout)
            if not isinstance(output, dict):
                raise RuntimeError(f"{language}: engine output must be a JSON object")
            expected = oracle(board, player)
            if (output.get("language") != language
                    or type(output.get("move")) is not int or type(output.get("score")) is not int
                    or (output["move"], output["score"]) != expected
                    or type(output.get("nodes")) is not int or output["nodes"] < 1):
                raise RuntimeError(f"{language}: {board}/{player}: expected {expected}, received {output}")
        for board, player in invalid:
            completed = run([*argv, board, player])
            if completed.returncode != 2 or completed.stdout.strip() or not completed.stderr.strip():
                raise RuntimeError(f"{language}: invalid input {board}/{player} violated exit/stderr contract")
        coverage[language] = {"positions": len(cases), "invalid_inputs": len(invalid)}
    return coverage


def exhaustive_python() -> int:
    spec = importlib.util.spec_from_file_location("arena_reference_under_test", ROOT / "python/main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    positions = reachable()
    for board, player in positions:
        actual = module.solve(board, player)
        if (actual["move"], actual["score"]) != oracle(board, player):
            raise RuntimeError(f"python: exhaustive mismatch at {board}/{player}")
    return len(positions)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--languages", nargs="+", choices=LANGUAGES, default=list(LANGUAGES))
    parser.add_argument("--cases", type=int, default=32)
    parser.add_argument("--exhaustive-python", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if not 4 <= args.cases <= 4520 or len(set(args.languages)) != len(args.languages):
        parser.error("cases must be between 4 and 4520; languages must be unique")
    try:
        pool = reachable()
        mandatory = [("---------", "X"), ("XX-OO----", "X"),
                     ("OO-XX-X--", "O"), ("X--------", "O")]
        others = [case for case in pool if case not in mandatory]
        cases = mandatory + random.Random(17).sample(others, args.cases - len(mandatory))
        with tempfile.TemporaryDirectory(prefix="arena-contract-") as directory:
            coverage = verify(engines(args.languages, Path(directory)), cases)
        report = {"seed": 17, "oracle": "unpruned exhaustive minimax",
                  "coverage": coverage, "all_eight_languages": set(args.languages) == set(LANGUAGES)}
        sources = {"python": "python/main.py", "javascript": "javascript/main.js",
                   "c": "c/main.c", "cpp": "cpp/main.cpp", "java": "java/Main.java",
                   "php": "php/main.php", "csharp": "csharp/Program.cs", "swift": "swift/main.swift"}
        paths = [sources[language] for language in args.languages] + ["scripts/verify_contract.py"]
        report["source_sha256"] = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                                   for path in paths}
        report["corpus"] = [{"board": board, "player": player, "move": oracle(board, player)[0],
                             "score": oracle(board, player)[1]} for board, player in cases]
        if args.exhaustive_python:
            report["exhaustive_python_positions"] = exhaustive_python()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, sort_keys=True))
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"contract verification failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
