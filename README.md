# Polyglot Alpha-Beta Arena

A small decision engine implemented in **eight programming languages**:

- Python
- JavaScript
- C
- C++
- Java
- PHP
- C#
- Swift

Each implementation solves the same Tic-Tac-Toe position using **minimax with alpha-beta pruning** and returns the result through one shared JSON protocol.

This is deliberately a compact project: the interesting part is not Tic-Tac-Toe itself, but demonstrating that the same algorithm, interfaces, validation rules, and CI contract can be expressed consistently across different language ecosystems.

## Example

Input:

```text
board:  XX-OO----
player: X
```

Board indexes:

```text
0 | 1 | 2
---------
3 | 4 | 5
---------
6 | 7 | 8
```

Expected result: X selects index `2` and wins immediately.

```json
{"language":"python","move":2,"score":9,"nodes":64}
```

`nodes` may vary between implementations or future optimizations, but `move` and `score` must agree.

## Why this is useful as a portfolio project

It demonstrates:

- algorithmic reasoning
- minimax and alpha-beta pruning
- recursion and state rollback
- deterministic tie-breaking
- command-line interface design
- input validation and error handling
- JSON interoperability
- cross-language CI on Linux and macOS

It is small enough to explain in an interview without pretending to be a production AI platform.

## Unified interface

Every implementation accepts:

```text
<board> <player>
```

- `board`: exactly nine characters using `X`, `O`, and `-`
- `player`: `X` or `O`, representing the AI player whose move is requested

All implementations print one JSON object:

```json
{"language":"cpp","move":2,"score":9,"nodes":64}
```

Invalid input is written to stderr and exits with status code `2`.

## Run locally

### Python

```bash
python3 python/main.py XX-OO---- X
```

### JavaScript

```bash
node javascript/main.js XX-OO---- X
```

### C

```bash
gcc -std=c17 -O2 c/main.c -o alpha-c
./alpha-c XX-OO---- X
```

### C++

```bash
g++ -std=c++20 -O2 cpp/main.cpp -o alpha-cpp
./alpha-cpp XX-OO---- X
```

### Java

```bash
javac java/Main.java
java -cp java Main XX-OO---- X
```

### PHP

```bash
php php/main.php XX-OO---- X
```

### C#

```bash
dotnet run --project csharp/PolyglotAlphaBeta.csproj -- XX-OO---- X
```

### Swift

```bash
swiftc swift/main.swift -O -o alpha-swift
./alpha-swift XX-OO---- X
```

## Algorithm

For every legal move, the engine:

1. applies the candidate move;
2. recursively explores the opponent response;
3. scores wins, losses, and draws;
4. rolls the board state back;
5. prunes branches that cannot improve the result;
6. selects the lowest board index when scores are tied.

The worst-case game-tree complexity is exponential, but alpha-beta pruning reduces the number of explored states when strong moves are evaluated early.

## Continuous integration

GitHub Actions compiles and runs all eight implementations. A comparison script verifies that every language agrees on the selected move and score.

## Possible extensions

- add Connect Four with the same protocol;
- benchmark node counts and execution time;
- add transposition tables;
- expose the engine through a small web visualizer;
- generate property-based test positions;
- compare minimax against Monte Carlo Tree Search.

## Status

**MVP complete.** The project is intentionally narrow and reviewable. Future additions should preserve the common protocol and cross-language tests.
