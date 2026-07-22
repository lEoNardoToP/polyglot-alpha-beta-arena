package ai.mechanics;

import java.util.Arrays;
import java.util.Random;

public final class NeuralNetwork {
    private final int inputSize, hiddenSize, outputSize;
    private final double[][] weights1, weights2;
    private final double[] bias1, bias2;

    public NeuralNetwork(int inputSize, int hiddenSize, int outputSize, long seed) {
        this.inputSize = inputSize; this.hiddenSize = hiddenSize; this.outputSize = outputSize;
        this.weights1 = new double[hiddenSize][inputSize]; this.bias1 = new double[hiddenSize];
        this.weights2 = new double[outputSize][hiddenSize]; this.bias2 = new double[outputSize];
        initialize(new Random(seed));
    }

    public double[] predict(double[] input) {
        requireInput(input);
        return outputActivation(hiddenActivation(input));
    }

    public double train(double[] input, double[] target, double learningRate) {
        requireInput(input);
        if (target.length != outputSize) throw new IllegalArgumentException("Target width does not match network output");
        double[] hiddenPre = new double[hiddenSize], hidden = new double[hiddenSize];
        for (int h = 0; h < hiddenSize; h++) {
            double sum = bias1[h];
            for (int i = 0; i < inputSize; i++) sum += weights1[h][i] * input[i];
            hiddenPre[h] = sum; hidden[h] = Math.max(0.0, sum);
        }
        double[] output = outputActivation(hidden), outputGradient = new double[outputSize];
        double loss = 0.0;
        for (int o = 0; o < outputSize; o++) {
            double error = output[o] - target[o];
            loss += huber(error); outputGradient[o] = huberDerivative(error) / outputSize;
        }
        double[] hiddenGradient = new double[hiddenSize];
        for (int h = 0; h < hiddenSize; h++) {
            double gradient = 0.0;
            for (int o = 0; o < outputSize; o++) gradient += weights2[o][h] * outputGradient[o];
            hiddenGradient[h] = hiddenPre[h] > 0.0 ? gradient : 0.0;
        }
        for (int o = 0; o < outputSize; o++) {
            for (int h = 0; h < hiddenSize; h++) weights2[o][h] -= learningRate * outputGradient[o] * hidden[h];
            bias2[o] -= learningRate * outputGradient[o];
        }
        for (int h = 0; h < hiddenSize; h++) {
            for (int i = 0; i < inputSize; i++) weights1[h][i] -= learningRate * hiddenGradient[h] * input[i];
            bias1[h] -= learningRate * hiddenGradient[h];
        }
        return loss / outputSize;
    }

    public void copyFrom(NeuralNetwork source) {
        if (source.inputSize != inputSize || source.hiddenSize != hiddenSize || source.outputSize != outputSize)
            throw new IllegalArgumentException("Network shapes must match");
        for (int h = 0; h < hiddenSize; h++) System.arraycopy(source.weights1[h], 0, weights1[h], 0, inputSize);
        System.arraycopy(source.bias1, 0, bias1, 0, hiddenSize);
        for (int o = 0; o < outputSize; o++) System.arraycopy(source.weights2[o], 0, weights2[o], 0, hiddenSize);
        System.arraycopy(source.bias2, 0, bias2, 0, outputSize);
    }

    private void initialize(Random random) {
        double firstScale = Math.sqrt(2.0 / inputSize), secondScale = Math.sqrt(2.0 / hiddenSize);
        for (int h = 0; h < hiddenSize; h++) for (int i = 0; i < inputSize; i++) weights1[h][i] = random.nextGaussian() * firstScale;
        for (int o = 0; o < outputSize; o++) for (int h = 0; h < hiddenSize; h++) weights2[o][h] = random.nextGaussian() * secondScale;
    }

    private double[] hiddenActivation(double[] input) {
        double[] hidden = new double[hiddenSize];
        for (int h = 0; h < hiddenSize; h++) {
            double sum = bias1[h];
            for (int i = 0; i < inputSize; i++) sum += weights1[h][i] * input[i];
            hidden[h] = Math.max(0.0, sum);
        }
        return hidden;
    }

    private double[] outputActivation(double[] hidden) {
        double[] output = Arrays.copyOf(bias2, outputSize);
        for (int o = 0; o < outputSize; o++) for (int h = 0; h < hiddenSize; h++) output[o] += weights2[o][h] * hidden[h];
        return output;
    }

    private void requireInput(double[] input) { if (input.length != inputSize) throw new IllegalArgumentException("Input width does not match network input"); }
    private static double huber(double error) { double absolute = Math.abs(error); return absolute <= 1.0 ? 0.5 * error * error : absolute - 0.5; }
    private static double huberDerivative(double error) { return error > 1.0 ? 1.0 : error < -1.0 ? -1.0 : error; }
}
