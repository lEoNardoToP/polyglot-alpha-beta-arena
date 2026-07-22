package ai.mechanics;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public final class GridWorld {
    public static final int UP = 0, RIGHT = 1, DOWN = 2, LEFT = 3, ACTIONS = 4;
    public record Step(double[] state, double reward, boolean terminal) {}

    private final int size;
    private final int goal;
    private final Set<Integer> walls;
    private final Set<Integer> hazards;
    private int position;

    public GridWorld() { this(6); }

    public GridWorld(int size) {
        if (size < 4) throw new IllegalArgumentException("Grid size must be at least 4");
        this.size = size;
        this.goal = index(size - 1, size - 1);
        this.walls = new HashSet<>(Arrays.asList(index(1, 1), index(1, 2), index(2, 2), index(3, 3), index(4, 1)));
        this.hazards = new HashSet<>(Arrays.asList(index(1, 4), index(3, 1), index(4, 3)));
        reset();
    }

    public double[] reset() { position = 0; return encode(position); }

    public Step step(int action) {
        if (action < 0 || action >= ACTIONS) throw new IllegalArgumentException("Unknown action: " + action);
        int row = position / size, column = position % size;
        int nextRow = row, nextColumn = column;
        switch (action) {
            case UP -> nextRow--;
            case RIGHT -> nextColumn++;
            case DOWN -> nextRow++;
            case LEFT -> nextColumn--;
            default -> throw new IllegalStateException("Unreachable action");
        }
        double reward = -0.02;
        if (nextRow < 0 || nextRow >= size || nextColumn < 0 || nextColumn >= size) reward = -0.08;
        else {
            int candidate = index(nextRow, nextColumn);
            if (walls.contains(candidate)) reward = -0.08;
            else position = candidate;
        }
        if (hazards.contains(position)) return new Step(encode(position), -1.0, true);
        if (position == goal) return new Step(encode(position), 1.0, true);
        return new Step(encode(position), reward, false);
    }

    public int stateSize() { return size * size; }
    public int size() { return size; }
    public boolean isWall(int row, int column) { return walls.contains(index(row, column)); }
    public boolean isHazard(int row, int column) { return hazards.contains(index(row, column)); }
    public boolean isGoal(int row, int column) { return index(row, column) == goal; }
    public double[] stateFor(int row, int column) { return encode(index(row, column)); }
    private int index(int row, int column) { return row * size + column; }
    private double[] encode(int state) { double[] encoded = new double[stateSize()]; encoded[state] = 1.0; return encoded; }
}
