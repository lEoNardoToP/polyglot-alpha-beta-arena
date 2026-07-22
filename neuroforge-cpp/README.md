# NeuroForge C++

A dependency-free neural-network engine that exposes the mechanics normally hidden by PyTorch or TensorFlow.

## What it demonstrates

- reverse-mode automatic differentiation over a dynamic computation graph;
- correct gradient accumulation when values are reused in a graph;
- composable differentiable operators (`+`, `*`, `pow`, `exp`, `log`, `tanh`, `ReLU`);
- multilayer perceptrons with Xavier initialization;
- binary cross-entropy and the Adam optimizer;
- finite-difference gradient checking before training;
- real nonlinear classification on a noisy two-moons dataset.

## Run

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
./build/neuroforge_demo
```

The demo trains a `2 → 16 → 16 → 1` network and prints an ASCII decision boundary. No ML library is used.

## Architecture

`Value` stores data, gradient, graph parents, and a local derivative closure. `backward()` topologically orders the graph and applies the chain rule in reverse. `Neuron`, `Layer`, and `MLP` compose these scalar nodes, while `Adam` updates the leaf parameters.

This is intentionally small enough to audit: every derivative and optimizer state transition can be followed directly in the source.
