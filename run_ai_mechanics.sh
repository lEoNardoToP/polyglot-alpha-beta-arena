#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

cmake -S "$ROOT/neuroforge-cpp" -B "$ROOT/neuroforge-cpp/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$ROOT/neuroforge-cpp/build" --parallel 2
ctest --test-dir "$ROOT/neuroforge-cpp/build" --output-on-failure
"$ROOT/neuroforge-cpp/build/neuroforge_demo"

"$ROOT/deepgrid-java/build.sh"
