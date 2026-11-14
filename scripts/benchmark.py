#!/usr/bin/env python3
"""Benchmark verified CLI engines on a fixed corpus; timings include process startup."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

import verify_contract as contract

ROOT = contract.ROOT
CORPUS = ROOT / "benchmark/corpus.json"
SOURCES = {"python": "python/main.py", "javascript": "javascript/main.js",
           "c": "c/main.c", "cpp": "cpp/main.cpp", "java": "java/Main.java",
           "php": "php/main.php", "csharp": "csharp/Program.cs", "swift": "swift/main.swift"}
VERSION_COMMANDS = {"python": [sys.executable, "--version"], "javascript": ["node", "--version"],
                    "c": ["cc", "--version"], "cpp": ["c++", "--version"],
                    "java": ["java", "-version"], "php": ["php", "--version"],
                    "csharp": ["dotnet", "--version"], "swift": ["swiftc", "--version"]}


def load_corpus(path: Path = CORPUS) -> list[dict]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError("unsupported corpus version")
    positions = document.get("positions")
    if not isinstance(positions, list) or not positions:
        raise ValueError("corpus must contain positions")
    legal = set(contract.reachable())
    names, boards = set(), set()
    for case in positions:
        if not isinstance(case, dict) or any(not isinstance(case.get(k), str)
                                             for k in ("name", "board", "player")):
            raise ValueError("each corpus entry needs a name, board and player")
        pair = (case["board"], case["player"])
        if not case["name"] or case["name"] in names or pair in boards or pair not in legal:
            raise ValueError(f"duplicate or unreachable corpus entry: {case}")
        names.add(case["name"])
        boards.add(pair)
    return positions


@lru_cache(maxsize=None)
def full_tree_nodes(board: str, turn: str) -> int:
    """Count all visits in unpruned minimax, including this node and all branches.

    Caching accelerates the counting calculation; the returned count still includes
    repeated visits to transpositions. This function is not a timed engine.
    """
    if contract.winner(board) or "-" not in board:
        return 1
    return 1 + sum(full_tree_nodes(board[:i] + turn + board[i + 1:],
                                  "O" if turn == "X" else "X")
                   for i, cell in enumerate(board) if cell == "-")


def checked_output(completed, language: str, board: str, player: str) -> dict:
    if completed.returncode:
        raise ValueError(f"{language}: engine exited {completed.returncode}: {completed.stderr[:300]}")
    output = json.loads(completed.stdout)
    if (not isinstance(output, dict) or output.get("language") != language
            or type(output.get("move")) is not int or type(output.get("score")) is not int
            or type(output.get("nodes")) is not int or output["nodes"] < 1
            or (output["move"], output["score"]) != contract.oracle(board, player)):
        raise ValueError(f"{language}: output violates the oracle contract: {output}")
    return {key: output[key] for key in ("move", "score", "nodes")}


def measure(commands: dict[str, list[str]], cases: list[dict], repeats: int) -> dict:
    results = {}
    for language, command in commands.items():
        rows = []
        for case in cases:
            board, player = case["board"], case["player"]
            argv = [*command, board, player]
            # One verified warmup per case; compilation and oracle work are untimed.
            expected = checked_output(contract.run(argv), language, board, player)
            elapsed = []
            for _ in range(repeats):
                start = time.perf_counter_ns()
                completed = contract.run(argv)
                duration = time.perf_counter_ns() - start
                actual = checked_output(completed, language, board, player)
                if actual != expected:
                    raise ValueError(f"{language}: nondeterministic result for {case['name']}")
                elapsed.append(duration / 1_000_000)
            # Engines count recursive calls beneath the root move loop.
            unpruned = full_tree_nodes(board, player) - 1
            rows.append({**case, **expected, "unpruned_nodes": unpruned,
                         "node_reduction_fraction": 1 - expected["nodes"] / unpruned,
                         "cli_ms_samples": elapsed,
                         "cli_ms_median": statistics.median(elapsed)})
        results[language] = rows
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--languages", nargs="+", choices=contract.LANGUAGES,
                        default=list(contract.LANGUAGES))
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not 1 <= args.repeats <= 100 or len(set(args.languages)) != len(args.languages):
        parser.error("repeats must be 1..100; languages must be unique")
    try:
        cases = load_corpus()
        with tempfile.TemporaryDirectory(prefix="arena-benchmark-") as directory:
            commands = contract.engines(args.languages, Path(directory))
            results = measure(commands, cases, args.repeats)
        paths = [SOURCES[language] for language in args.languages]
        if "csharp" in args.languages:
            paths.append("csharp/PolyglotAlphaBeta.csproj")
        paths += ["scripts/benchmark.py", "scripts/verify_contract.py", "benchmark/corpus.json"]
        toolchains = {}
        for language in args.languages:
            version = contract.run(VERSION_COMMANDS[language])
            toolchains[language] = {"argv": VERSION_COMMANDS[language], "exit_code": version.returncode,
                                    "version": (version.stdout + version.stderr).strip()[:2000]}
        report = {
            "schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "environment": {"platform": platform.platform(), "machine": platform.machine(),
                            "python": platform.python_version(), "logical_cpus": os.cpu_count()},
            "toolchains": toolchains,
            "method": {"repeats": args.repeats, "warmups_per_case": 1,
                       "timing": "wall-clock CLI latency including process startup; excludes compilation and oracle",
                       "node_baseline": "unpruned full tree excluding synthetic root; transpositions counted per visit",
                       "limits": "small fixed corpus; shared host; no pure search throughput or production claims"},
            "languages": args.languages,
            "all_eight_languages": set(args.languages) == set(contract.LANGUAGES),
            "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
            "results": results,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Verified {len(cases)} positions across {len(results)} languages; wrote {args.output}")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"benchmark failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
