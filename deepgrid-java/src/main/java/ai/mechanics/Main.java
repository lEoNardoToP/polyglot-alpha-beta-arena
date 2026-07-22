package ai.mechanics;

import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;

public final class Main {
    private static final int MAX_STEPS = 70;
    private Main() {}

    public static void main(String[] args) {
        GridWorld environment = new GridWorld();
        DqnAgent agent = new DqnAgent(environment.stateSize(), 42);
        Deque<Double> recentRewards = new ArrayDeque<>();
        Deque<Integer> recentSuccesses = new ArrayDeque<>();
        System.out.println("DeepGrid Java - DQN implemented without ML libraries");

        for (int episode = 1; episode <= 2_000; episode++) {
            double[] state = environment.reset();
            double episodeReward = 0.0;
            boolean success = false;
            double latestLoss = Double.NaN;
            for (int step = 0; step < MAX_STEPS; step++) {
                int action = agent.selectAction(state, true);
                GridWorld.Step outcome = environment.step(action);
                agent.remember(state, action, outcome.reward(), outcome.state(), outcome.terminal());
                latestLoss = agent.learn();
                state = outcome.state();
                episodeReward += outcome.reward();
                if (outcome.terminal()) { success = outcome.reward() > 0.0; break; }
            }
            agent.finishEpisode();
            push(recentRewards, episodeReward, 100);
            push(recentSuccesses, success ? 1 : 0, 100);
            if (episode == 1 || episode % 200 == 0) {
                double successRate = recentSuccesses.stream().mapToInt(Integer::intValue).average().orElse(0.0);
                double meanReward = recentRewards.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
                System.out.printf("episode=%4d epsilon=%.3f avg_reward=%+.3f success_100=%5.1f%% loss=%s%n",
                        episode, agent.epsilon(), meanReward, successRate * 100.0,
                        Double.isNaN(latestLoss) ? "warming-up" : String.format("%.5f", latestLoss));
            }
        }

        double evaluationSuccess = evaluate(environment, agent, 200);
        System.out.printf("%nGreedy evaluation success: %.1f%%%n", evaluationSuccess * 100.0);
        System.out.println("Q-values at start [up, right, down, left]: " + Arrays.toString(agent.qValues(environment.reset())));
        printPolicy(environment, agent);
        if (evaluationSuccess < 0.90) throw new IllegalStateException("The learned policy did not reach the expected success rate");
    }

    private static double evaluate(GridWorld environment, DqnAgent agent, int episodes) {
        int successes = 0;
        for (int episode = 0; episode < episodes; episode++) {
            double[] state = environment.reset();
            for (int step = 0; step < MAX_STEPS; step++) {
                GridWorld.Step outcome = environment.step(agent.greedyAction(state));
                state = outcome.state();
                if (outcome.terminal()) { successes += outcome.reward() > 0.0 ? 1 : 0; break; }
            }
        }
        return successes / (double) episodes;
    }

    private static void printPolicy(GridWorld environment, DqnAgent agent) {
        char[] arrows = {'^', '>', 'v', '<'};
        System.out.println("\nLearned greedy policy:");
        for (int row = 0; row < environment.size(); row++) {
            for (int column = 0; column < environment.size(); column++) {
                char symbol;
                if (row == 0 && column == 0) symbol = 'S';
                else if (environment.isWall(row, column)) symbol = '#';
                else if (environment.isHazard(row, column)) symbol = 'X';
                else if (environment.isGoal(row, column)) symbol = 'G';
                else symbol = arrows[agent.greedyAction(environment.stateFor(row, column))];
                System.out.print(symbol + " ");
            }
            System.out.println();
        }
    }

    private static <T> void push(Deque<T> values, T value, int limit) {
        values.addLast(value);
        if (values.size() > limit) values.removeFirst();
    }
}
