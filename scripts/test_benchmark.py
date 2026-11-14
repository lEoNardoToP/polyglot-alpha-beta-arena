import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import benchmark


def response(nodes=1, move=0, score=0):
    return subprocess.CompletedProcess([], 0, json.dumps(
        {"language": "python", "nodes": nodes, "move": move, "score": score}), "")


class BenchmarkTests(unittest.TestCase):
    def test_corpus_rejects_wrong_turn_and_duplicates(self):
        original = json.loads(benchmark.CORPUS.read_text())
        for corruption in ("wrong-turn", "duplicate"):
            document = copy.deepcopy(original)
            if corruption == "wrong-turn":
                document["positions"][0]["player"] = "O"
            else:
                document["positions"].append(document["positions"][0])
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "corpus.json"
                path.write_text(json.dumps(document))
                with self.assertRaises(ValueError):
                    benchmark.load_corpus(path)

    def test_unpruned_count_includes_every_visit(self):
        # One legal move remains and ends in a draw.
        self.assertEqual(benchmark.full_tree_nodes("-OOOXXXXO", "X"), 2)
        self.assertEqual(benchmark.full_tree_nodes("---------", "X") - 1, 549945)

    def test_forged_output_cannot_be_benchmarked(self):
        for completed in (response(move=1), response(nodes=True), response(score=False),
                          subprocess.CompletedProcess([], 2, "", "failure"),
                          subprocess.CompletedProcess([], 0, "[]", "")):
            with self.subTest(output=completed.stdout), self.assertRaises(ValueError):
                benchmark.checked_output(completed, "python", "-OOOXXXXO", "X")

    def test_measure_excludes_warmup_and_checks_every_sample(self):
        case = {"name": "last", "board": "-OOOXXXXO", "player": "X"}
        with patch.object(benchmark.contract, "run", return_value=response()) as run:
            result = benchmark.measure({"python": ["engine"]}, [case], 3)["python"][0]
        self.assertEqual(run.call_count, 4)
        self.assertEqual(len(result["cli_ms_samples"]), 3)
        self.assertEqual(result["unpruned_nodes"], 1)
        self.assertEqual(result["node_reduction_fraction"], 0)
        with patch.object(benchmark.contract, "run", side_effect=[response(), response(nodes=2)]):
            with self.assertRaisesRegex(ValueError, "nondeterministic"):
                benchmark.measure({"python": ["engine"]}, [case], 1)


if __name__ == "__main__":
    unittest.main()
