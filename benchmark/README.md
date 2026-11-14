# Measure the search, verify the answer

This benchmark makes two different observations explicit:

- **Search work:** recursive node visits compared with the full unpruned game tree.
- **CLI latency:** wall-clock time for a fresh process to return an answer, including startup.

It is a small, fixed tic-tac-toe experiment, not a production performance claim.
In particular, CLI latency must not be described as pure search throughput or used
to claim that one language is intrinsically faster than another.

## Reproduce

From the repository root, with Python 3.10+, Node, a C compiler and a C++ compiler:

```bash
python3 scripts/benchmark.py --languages python javascript c cpp \
  --repeats 5 --output benchmark/results/local.json
```

The default requires all eight toolchains. Select a local subset explicitly;
missing compilers fail rather than silently shrinking the experiment. C and C++
use the same `-O2` build path as the contract verifier. Build commands live in
[`verify_contract.py`](../scripts/verify_contract.py).

The committed [`corpus.json`](corpus.json) contains eight named, reachable
nonterminal positions: opening responses, an immediate win, a forced block,
opposite corners and late-game cases. It is intentionally small and does not
replace the separate 4,520-position Python correctness check.

## What is checked

Every warmup and measured answer must match the independent, unpruned oracle's
move and score. JSON field types, language and a positive node count are checked.
Repeated runs must return identical move, score and node count. Incorrect output,
unreachable corpus entries, missing tools, build failures and timeouts fail the run.
An output file is written only after all checks pass; on failure an older file at
that path is left untouched, so check the exit status before treating it as fresh.

Compilation, corpus validation, oracle work and JSON validation are outside the
timed region. Each position gets one warmup followed by the requested number of
fresh process launches. Raw samples and the median are retained; no unstable
timing threshold gates CI. The workflow uploads a fresh benchmark artifact.

The node baseline counts every full-tree visit, including repeated visits to the
same board. It excludes the synthetic root because the engines count only calls
beneath their root move loop. The baseline's counting function uses caching to
compute that total efficiently; it is not itself a timed competing engine.

## Recorded evidence

[`results/local-2026-11-14.json`](results/local-2026-11-14.json) records an executed
run on a shared Linux x86_64 host with four languages, eight positions and five
measured samples per position: **160 checked samples plus 32 checked warmups**.
Java, PHP, C# and Swift were not measured in that run.

On the empty board, with the same move ordering and root search strategy:

| Implementation | Recursive visits | Reduction vs. full tree |
|:--|--:|--:|
| Unpruned tree baseline | 549,945 | — |
| C / C++ / JavaScript alpha-beta | 34,202 | 93.8% |
| Python alpha-beta + transposition table | 8,482 | 98.5% |

The Python change reduces visits by approximately **75.2%** relative to its
previous 34,202 visits. The executed
[`before` report](results/before-transpositions-2026-11-14.json) retains the
original Python source hash. These are deterministic work counts, not wall-clock
speedups. Full samples, toolchain versions, environment metadata, UTC timestamp
and source/corpus SHA-256 hashes are in both JSON files.

### Why the table preserves the answer

The Python engine shares a table across root branches within one `solve` call.
Keys include board, current player, perspective and depth. Entries distinguish
exact values, lower bounds and upper bounds: an alpha-beta cutoff cannot be
reused as an exact answer. Cached bounds tighten later search windows; the table
is discarded at the end of the call. The root still visits cells in index order
and updates only on a strictly better score, preserving lowest-index tie breaks.

Validation includes narrow-window bound reuse tests and the independent oracle
over all **4,520 reachable nonterminal positions** for Python. The four-language
CLI check also covers 32 positions and six invalid inputs per implementation.

To inspect the opening result without extra dependencies:

```bash
python3 - <<'PY'
import json
with open('benchmark/results/local-2026-11-14.json') as file:
    report = json.load(file)
for language, rows in report['results'].items():
    row = rows[0]
    print(language, 'nodes:', row['nodes'], 'CLI median ms:', row['cli_ms_median'])
PY
```
