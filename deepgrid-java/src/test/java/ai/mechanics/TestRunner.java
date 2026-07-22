package ai.mechanics;

public final class TestRunner {
    private static int failures;
    private TestRunner() {}

    public static void main(String[] args) {
        testEnvironmentPath();
        testReplayBufferCapacity();
        testNetworkLearnsOneExample();
        if (failures > 0) throw new AssertionError(failures + " tests failed");
        System.out.println("All Java DQN tests passed.");
    }

    private static void testEnvironmentPath() {
        GridWorld environment = new GridWorld();
        environment.reset();
        GridWorld.Step step = null;
        for (int i = 0; i < 5; i++) step = environment.step(GridWorld.RIGHT);
        for (int i = 0; i < 5; i++) step = environment.step(GridWorld.DOWN);
        check(step != null && step.terminal() && step.reward() == 1.0, "known safe path should reach goal");
    }

    private static void testReplayBufferCapacity() {
        ReplayBuffer buffer = new ReplayBuffer(3);
        double[] state = {1.0, 0.0};
        for (int i = 0; i < 10; i++) buffer.add(state, 0, i, state, false);
        check(buffer.size() == 3, "replay buffer should retain its fixed capacity");
    }

    private static void testNetworkLearnsOneExample() {
        NeuralNetwork network = new NeuralNetwork(3, 8, 2, 5);
        double[] input = {1.0, 0.0, 0.0}, target = {0.75, -0.25};
        double before = squaredError(network.predict(input), target);
        for (int i = 0; i < 500; i++) network.train(input, target, 0.03);
        double after = squaredError(network.predict(input), target);
        check(after < before * 0.02, "backpropagation should reduce prediction error");
    }

    private static double squaredError(double[] prediction, double[] target) {
        double result = 0.0;
        for (int i = 0; i < prediction.length; i++) { double error = prediction[i] - target[i]; result += error * error; }
        return result;
    }

    private static void check(boolean condition, String message) {
        if (!condition) { System.err.println("FAIL: " + message); failures++; }
    }
}
