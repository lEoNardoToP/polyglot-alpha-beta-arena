package ai.mechanics;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public final class ReplayBuffer {
    public record Transition(double[] state, int action, double reward, double[] nextState, boolean terminal) {}
    private final Transition[] entries;
    private int size, cursor;

    public ReplayBuffer(int capacity) {
        if (capacity <= 0) throw new IllegalArgumentException("Capacity must be positive");
        entries = new Transition[capacity];
    }

    public void add(double[] state, int action, double reward, double[] nextState, boolean terminal) {
        entries[cursor] = new Transition(state.clone(), action, reward, nextState.clone(), terminal);
        cursor = (cursor + 1) % entries.length;
        size = Math.min(size + 1, entries.length);
    }

    public List<Transition> sample(int batchSize, Random random) {
        if (batchSize > size) throw new IllegalArgumentException("Cannot sample more transitions than stored");
        List<Transition> result = new ArrayList<>(batchSize);
        for (int i = 0; i < batchSize; i++) result.add(entries[random.nextInt(size)]);
        return result;
    }

    public int size() { return size; }
    public int capacity() { return entries.length; }
}
