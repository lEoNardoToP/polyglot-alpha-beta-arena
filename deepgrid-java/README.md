# DeepGrid Java

A Deep Q-Network that learns a navigation policy in a hazardous GridWorld, implemented in plain Java with no machine-learning framework.

## What it demonstrates

- a Markov decision process with state, action, reward and terminal transitions;
- epsilon-greedy exploration and exploitation;
- a neural Q-function trained by manual backpropagation;
- Bellman targets and discounted future reward;
- experience replay to reduce temporal correlation;
- a separate target network to stabilize bootstrapping;
- Huber loss, He initialization and deterministic experiments;
- evaluation separated from training.

## Run

```bash
./build.sh
```

The program trains the agent, reports rolling reward and success rate, evaluates a greedy policy, and prints the action selected in every cell.

## Why DQN matters

Unlike a scripted shortest-path solver, the agent is never given the correct route. It discovers a policy from delayed rewards while balancing exploration against exploitation. The online network estimates `Q(state, action)`; the target network supplies a slowly changing objective:

```text
target = reward + gamma * max_a Q_target(next_state, a)
```

Everything from matrix operations to gradient updates and replay sampling is visible in the source.
