"""Independent golden cases and negative controls for the contract checker."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from verify_contract import oracle, reachable, verify


class ContractTests(unittest.TestCase):
    def test_known_game_outcomes(self):
        self.assertEqual(oracle("---------", "X"), (0, 0))
        self.assertEqual(oracle("XX-OO----", "X"), (2, 9))
        self.assertEqual(oracle("OO-XX-X--", "O"), (2, 9))
        self.assertEqual(oracle("X--------", "O"), (4, 0))

    def test_corpus_contains_only_reachable_nonterminal_turns(self):
        positions = reachable()
        self.assertEqual(len(positions), 4520)
        self.assertEqual(len(set(positions)), len(positions))
        for board, turn in positions:
            self.assertIn("-", board)
            self.assertEqual(board.count("X") - board.count("O"), 0 if turn == "X" else 1)

    def test_engines_agreeing_on_wrong_answer_are_rejected(self):
        # The previous comparison could pass if every engine shared the bug.
        with tempfile.TemporaryDirectory() as directory:
            engine = Path(directory) / "wrong.py"
            engine.write_text("print(" + repr(json.dumps({
                "language": "python", "move": 2, "score": 9, "nodes": 1
            })) + ")\n")
            with self.assertRaisesRegex(RuntimeError, "expected"):
                verify({"python": [sys.executable, str(engine)]}, [("---------", "X")])

    def test_engine_accepting_invalid_inputs_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = Path(directory) / "invalid.py"
            engine.write_text("print('accepted')\n")
            with self.assertRaisesRegex(RuntimeError, "invalid input"):
                verify({"python": [sys.executable, str(engine)]}, [])


if __name__ == "__main__":
    unittest.main()
