#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD="$ROOT/build"
rm -rf "$BUILD"
mkdir -p "$BUILD/main" "$BUILD/test"

find "$ROOT/src/main/java" -name '*.java' -print0 | xargs -0 javac -Werror -Xlint:all -d "$BUILD/main"
find "$ROOT/src/test/java" -name '*.java' -print0 | xargs -0 javac -Werror -Xlint:all -cp "$BUILD/main" -d "$BUILD/test"
java -cp "$BUILD/main:$BUILD/test" ai.mechanics.TestRunner
java -cp "$BUILD/main" ai.mechanics.Main
