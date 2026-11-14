import importlib.util
import unittest

import verify_contract as contract

spec = importlib.util.spec_from_file_location("python_engine", contract.ROOT / "python/main.py")
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


class TranspositionTests(unittest.TestCase):
    def test_narrow_window_bounds_are_safe_to_reuse(self):
        for alpha, beta, bound in ((-2, -1, "lower"), (1, 2, "upper"), (-1, 1, "exact")):
            with self.subTest(alpha=alpha, beta=beta):
                board = list("X--------")
                table = {}
                engine.minimax(board, "O", "X", 1, alpha, beta, [0], table)
                self.assertEqual(table[("X--------", "O", "X", 1)][1], bound)
                self.assertEqual(engine.minimax(board, "O", "X", 1, -100, 100, [0], table), 0)
                self.assertEqual(''.join(board), "X--------")

    def test_opening_reuses_work_without_changing_tie_break(self):
        first = engine.solve("---------", "X")
        self.assertEqual((first["move"], first["score"]), contract.oracle("---------", "X"))
        self.assertLess(first["nodes"], 34202)  # Same traversal without the table.
        engine.solve("XX-OO----", "X")
        self.assertEqual(first, engine.solve("---------", "X"))


if __name__ == "__main__":
    unittest.main()
