# AI Mechanics: two from-scratch MVPs

This repository also contains two independent, dependency-free AI implementations designed for technical interviews and code review.

| Project | Language | Core mechanics implemented | Deterministic result |
|---|---|---|---|
| [NeuroForge](./neuroforge-cpp) | C++20 | reverse-mode autodiff, computation graphs, MLP, BCE, Adam, gradient checking | 100% held-out accuracy on noisy two-moons data |
| [DeepGrid](./deepgrid-java) | Java 21 | DQN, manual backpropagation, Bellman targets, replay buffer, target network, epsilon-greedy policy | 100% greedy evaluation success |

These are not API wrappers. The derivatives, optimizer transitions, neural updates and reinforcement-learning loop are visible in the source.

Run both projects with:

```bash
./run_ai_mechanics.sh
```
