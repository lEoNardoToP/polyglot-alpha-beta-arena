# AI Algorithms Portfolio

[![AI mechanics CI](https://github.com/lEoNardoToP/polyglot-alpha-beta-arena/actions/workflows/ai-mechanics-ci.yml/badge.svg)](https://github.com/lEoNardoToP/polyglot-alpha-beta-arena/actions/workflows/ai-mechanics-ci.yml)
[![Cross-language CI](https://github.com/lEoNardoToP/polyglot-alpha-beta-arena/actions/workflows/ci.yml/badge.svg)](https://github.com/lEoNardoToP/polyglot-alpha-beta-arena/actions/workflows/ci.yml)

A compact, inspectable portfolio of AI/algorithmic systems where the mechanics are visible in source code rather than hidden behind model APIs.

## 5-minute reviewer path

If you are reviewing this for an interview or hiring decision:

1. **Run the AI mechanics:** `./run_ai_mechanics.sh`
2. **Inspect C++ autodiff / MLP:** [`neuroforge-cpp`](./neuroforge-cpp)
3. **Inspect the Java DQN:** [`deepgrid-java`](./deepgrid-java)
4. **Run one alpha-beta engine:** `python3 python/main.py XX-OO---- X`
5. **Check the cross-language contract:** every implementation must agree on `move` and `score`.

For the concepts and trade-offs behind the code, see [`TECHNICAL_INTERVIEW_NOTES.md`](./TECHNICAL_INTERVIEW_NOTES.md).

---

## What is inside

### NeuroForge C++

A small from-scratch neural-network mechanics project containing:

- reverse-mode autodiff;
- computation graphs;
- MLP training;
- binary cross-entropy;
- Adam optimization;
- gradient checking.

The point is not to compete with a framework. It is to make gradient flow and optimization directly reviewable.

### DeepGrid Java

A compact Deep Q-Network implementation containing:

- manual backpropagation;
- Bellman targets;
- replay buffer;
- target network;
- epsilon-greedy exploration.

The goal is to expose the mechanics behind a basic value-based RL loop in ordinary Java code.

### Polyglot Alpha-Beta Arena

Minimax with alpha-beta pruning implemented consistently in:

- Python
- JavaScript
- C
- C++
- Java
- PHP
- C#
- Swift

All implementations use one shared command-line contract and JSON output format.

---

## Shared protocol

Input:

```text
<board> <player>
```

- `board`: exactly nine characters using `X`, `O`, and `-`
- `player`: `X` or `O`

Example:

```bash
python3 python/main.py XX-OO---- X
```

Output:

```json
{"language":"python","move":2,"score":9,"nodes":64}
```

`nodes` may vary between implementations or future optimizations. `move` and `score` are the contract fields that must agree.

Invalid input is written to stderr and exits with status code `2`.

---

## Why this repository exists

This is deliberately **not** an API-wrapper portfolio. A reviewer should be able to inspect concrete evidence of:

- algorithmic reasoning;
- ML/RL mechanics implemented from scratch;
- recursion and state rollback;
- deterministic behavior;
- validation and error handling;
- cross-language interface design;
- automated build/test contracts.

The systems are intentionally small enough to explain without pretending that a portfolio exercise is a production ML platform.

---

## Run locally

### AI mechanics

```bash
./run_ai_mechanics.sh
```

### Alpha-beta implementations

```bash
python3 python/main.py XX-OO---- X
node javascript/main.js XX-OO---- X

gcc -std=c17 -O2 c/main.c -o alpha-c
./alpha-c XX-OO---- X

g++ -std=c++20 -O2 cpp/main.cpp -o alpha-cpp
./alpha-cpp XX-OO---- X

javac java/Main.java
java -cp java Main XX-OO---- X

php php/main.php XX-OO---- X

dotnet run --project csharp/PolyglotAlphaBeta.csproj -- XX-OO---- X

swiftc swift/main.swift -O -o alpha-swift
./alpha-swift XX-OO---- X
```

---

## Proof of work

The repository is expected to preserve these properties:

- the AI mechanics build and run through automated checks;
- the alpha-beta implementations compile/run in their supported CI environments;
- implementations agree on the shared move/score contract;
- repeated runs are deterministic for the same input;
- failures are explicit rather than silently returning malformed output.

A future `benchmark/` directory will make the reviewer-facing evidence more systematic with a fixed input corpus and raw result summaries.

---

## Technical notes

[`AI_MECHANICS.md`](./AI_MECHANICS.md) summarizes the two neural MVPs.

[`TECHNICAL_INTERVIEW_NOTES.md`](./TECHNICAL_INTERVIEW_NOTES.md) covers:

- reverse-mode autodiff;
- binary cross-entropy;
- Adam;
- DQN and Bellman targets;
- replay buffers and target networks;
- epsilon-greedy exploration;
- minimax and alpha-beta pruning;
- why the shared cross-language protocol matters.

---

## Known scope and next improvements

The current repository is an intentionally narrow portfolio project. Useful next improvements are:

- fixed benchmark corpus and result snapshots;
- property-based position generation;
- transposition tables;
- timing/node-count comparisons;
- a small visualizer;
- a short terminal/demo recording.

Large unrelated experiments should live elsewhere so this repository remains easy to review.
