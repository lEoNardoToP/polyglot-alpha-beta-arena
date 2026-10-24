# Independent game-contract acceptance — 24 October 2026

## Executed locally

On macOS 15.8.1 x86_64:

| Check | Result |
|---|---|
| Python against exhaustive independent minimax | all 4,520 reachable nonterminal positions passed |
| Python, JavaScript, C, C++, Java | each passed 32 shared positions and 6 invalid-input cases |
| Swift | passed the same 32 positions and 6 invalid-input cases |
| Contract-checker golden cases and negative controls | 4/4 unittest cases passed |
| C++ NeuroForge build/CTest/training demo and Java DeepGrid tests/training | `bash run_ai_mechanics.sh` completed successfully |

PHP and C# were **not executed locally** because those toolchains are absent.
The new CI jobs require those engines explicitly; no full eight-language pass
is inferred from the six local implementations.

## Why the checker changed

Previously the hosted workflow compared `move` and `score` for one board.
Agreement alone could pass when every implementation shared a defect. The new
checker builds expected results using an independent, unpruned recursive game
tree, while the engines use alpha-beta pruning. The independent value encoding
also checks preference for faster wins, delayed losses and the lowest-index
move on equal scores.

The deterministic corpus starts with four hand-picked positions and adds
seeded reachable positions; JSON evidence records every expected answer and
SHA-256 hashes of the engine and checker sources. Negative controls demonstrate
that engines agreeing on a wrong answer and engines accepting invalid inputs
are rejected by the checker.

## Reproduce

```bash
python3 scripts/verify_contract.py --languages python javascript c cpp java \
  --exhaustive-python --output reports/local-contract.json
python3 -m unittest discover -s scripts -p test_verify_contract.py -v
bash run_ai_mechanics.sh
```

The local Command Line Tools Swift SDK/compiler combination initially failed.
The successful Swift run selected Xcode only for that command:

```bash
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  python3 scripts/verify_contract.py --languages swift --output reports/swift-contract.json
```

The checker places Swift's module cache in its disposable build directory;
it does not change global Xcode selection or write to the user's module cache.
On a correctly matched default SDK/compiler, the environment override is unnecessary.

[Raw JSON contracts and AI mechanics transcript](evidence/2026-10-24/).
A successful small-grid DQN demonstration is not a claim about broad RL performance.
