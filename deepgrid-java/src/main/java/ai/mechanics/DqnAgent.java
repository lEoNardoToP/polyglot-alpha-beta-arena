package ai.mechanics;

import java.util.List;
import java.util.Random;

public final class DqnAgent {
    private final NeuralNetwork onlineNetwork, targetNetwork;
    private final ReplayBuffer replayBuffer;
    private final Random random;
    private final double gamma = 0.97, learningRate = 0.008, minimumEpsilon = 0.04, epsilonDecay = 0.996;
    private final int batchSize = 32, targetSyncInterval = 120;
    private double epsilon = 1.0;
    private long updates;

    public DqnAgent(int stateSize, long seed) {
        onlineNetwork = new NeuralNetwork(stateSize, 64, GridWorld.ACTIONS, seed);
        targetNetwork = new NeuralNetwork(stateSize, 64, GridWorld.ACTIONS, seed + 1);
        targetNetwork.copyFrom(onlineNetwork);
        replayBuffer = new ReplayBuffer(8_000);
        random = new Random(seed + 2);
    }

    public int selectAction(double[] state, boolean explore) {
        if (explore && random.nextDouble() < epsilon) return random.nextInt(GridWorld.ACTIONS);
        return argmax(onlineNetwork.predict(state));
    }

    public void remember(double[] state, int action, double reward, double[] nextState, boolean terminal) {
        replayBuffer.add(state, action, reward, nextState, terminal);
    }

    public double learn() {
        if (replayBuffer.size() < batchSize) return Double.NaN;
        List<ReplayBuffer.Transition> batch = replayBuffer.sample(batchSize, random);
        double totalLoss = 0.0;
        for (ReplayBuffer.Transition transition : batch) {
            double[] target = onlineNetwork.predict(transition.state());
            double bootstrap = transition.terminal() ? 0.0 : gamma * max(targetNetwork.predict(transition.nextState()));
            target[transition.action()] = transition.reward() + bootstrap;
            totalLoss += onlineNetwork.train(transition.state(), target, learningRate);
        }
        updates++;
        if (updates % targetSyncInterval == 0) targetNetwork.copyFrom(onlineNetwork);
        return totalLoss / batch.size();
    }

    public void finishEpisode() { epsilon = Math.max(minimumEpsilon, epsilon * epsilonDecay); }
    public double epsilon() { return epsilon; }
    public double[] qValues(double[] state) { return onlineNetwork.predict(state); }
    public int greedyAction(double[] state) { return argmax(onlineNetwork.predict(state)); }

    private static int argmax(double[] values) {
        int best = 0;
        for (int i = 1; i < values.length; i++) if (values[i] > values[best]) best = i;
        return best;
    }
    private static double max(double[] values) {
        double best = values[0];
        for (int i = 1; i < values.length; i++) best = Math.max(best, values[i]);
        return best;
    }
}
