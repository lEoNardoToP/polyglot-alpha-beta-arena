#!/usr/bin/env python3
"""Validate that JSON outputs agree on move and score."""
from __future__ import annotations

import json
import sys


def main() -> int:
    payloads = [json.loads(line) for line in sys.stdin if line.strip()]
    if not payloads:
        print('no outputs supplied', file=sys.stderr)
        return 2
    expected = (payloads[0]['move'], payloads[0]['score'])
    mismatches = [p for p in payloads if (p['move'], p['score']) != expected]
    if mismatches:
        print(json.dumps({'expected': expected, 'mismatches': mismatches}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps({'implementations': len(payloads), 'move': expected[0], 'score': expected[1]}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
