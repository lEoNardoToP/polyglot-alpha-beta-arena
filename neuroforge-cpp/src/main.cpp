#include "neuroforge/nn.hpp"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <random>
#include <utility>
#include <vector>

using neuroforge::Adam;
using neuroforge::MLP;
using neuroforge::Value;

struct Sample { double x; double y; double label; };

std::vector<Sample> make_two_moons(std::size_t count, double noise, unsigned seed) {
    std::mt19937 generator(seed);
    std::normal_distribution<double> perturbation(0.0, noise);
    std::uniform_real_distribution<double> angle(0.0, 3.14159265358979323846);
    std::vector<Sample> samples;
    samples.reserve(count);
    for (std::size_t i = 0; i < count / 2; ++i) {
        const double theta = angle(generator);
        samples.push_back({std::cos(theta) + perturbation(generator),
                           std::sin(theta) + perturbation(generator), 0.0});
        samples.push_back({1.0 - std::cos(theta) + perturbation(generator),
                           0.5 - std::sin(theta) + perturbation(generator), 1.0});
    }
    std::shuffle(samples.begin(), samples.end(), generator);
    return samples;
}

Value binary_cross_entropy(const Value& logit, double label) {
    constexpr double epsilon = 1e-9;
    const Value probability = logit.sigmoid();
    return -(Value(label) * (probability + epsilon).log() +
             Value(1.0 - label) * (Value(1.0) - probability + epsilon).log());
}

std::pair<double, double> evaluate(const MLP& model, const std::vector<Sample>& samples) {
    double total_loss = 0.0;
    std::size_t correct = 0;
    for (const auto& sample : samples) {
        const Value logit = model.scalar({sample.x, sample.y});
        const double probability = 1.0 / (1.0 + std::exp(-logit.data()));
        total_loss += -(sample.label * std::log(probability + 1e-9) +
                        (1.0 - sample.label) * std::log(1.0 - probability + 1e-9));
        correct += (probability >= 0.5) == (sample.label >= 0.5);
    }
    return {total_loss / static_cast<double>(samples.size()),
            static_cast<double>(correct) / static_cast<double>(samples.size())};
}

bool gradient_check() {
    Value x(1.25); Value y(-0.75);
    Value expression = (x * y + x.tanh()).pow(2.0);
    expression.backward();
    const double analytic = x.grad();
    constexpr double h = 1e-6;
    const auto function = [](double input) {
        const double inner = input * -0.75 + std::tanh(input);
        return inner * inner;
    };
    const double numeric = (function(1.25 + h) - function(1.25 - h)) / (2.0 * h);
    const double error = std::abs(analytic - numeric);
    std::cout << "Gradient check | analytic=" << analytic << " numeric=" << numeric
              << " abs_error=" << error << '\n';
    return error < 1e-6;
}

void print_boundary(const MLP& model) {
    std::cout << "\nLearned decision boundary (# = class 1, . = class 0)\n";
    for (int row = 0; row < 14; ++row) {
        const double y = 1.5 - row * (2.5 / 13.0);
        for (int column = 0; column < 36; ++column) {
            const double x = -1.5 + column * (4.0 / 35.0);
            std::cout << (model.scalar({x, y}).data() >= 0.0 ? '#' : '.');
        }
        std::cout << '\n';
    }
}

int main() {
    std::cout << "NeuroForge C++ - reverse-mode autodiff and neural training from scratch\n";
    if (!gradient_check()) {
        std::cerr << "Gradient check failed. Refusing to train with incorrect derivatives.\n";
        return 1;
    }
    const auto training_data = make_two_moons(160, 0.09, 7);
    const auto test_data = make_two_moons(80, 0.09, 91);
    MLP model(2, {16, 16, 1}, 42);
    Adam optimizer(model.parameters(), 0.025);
    constexpr int epochs = 140;
    for (int epoch = 1; epoch <= epochs; ++epoch) {
        Value mean_loss(0.0);
        for (const auto& sample : training_data)
            mean_loss = mean_loss + binary_cross_entropy(model.scalar({sample.x, sample.y}), sample.label);
        mean_loss = mean_loss / static_cast<double>(training_data.size());
        optimizer.zero_grad();
        mean_loss.backward();
        optimizer.step();
        if (epoch == 1 || epoch % 20 == 0) {
            const auto [loss, accuracy] = evaluate(model, test_data);
            std::cout << "epoch=" << std::setw(3) << epoch << " train_loss=" << std::fixed
                      << std::setprecision(4) << mean_loss.data() << " test_loss=" << loss
                      << " test_accuracy=" << std::setprecision(1) << accuracy * 100.0 << "%\n";
        }
    }
    const auto [loss, accuracy] = evaluate(model, test_data);
    std::cout << "\nFinal test loss: " << std::setprecision(4) << loss
              << " | accuracy: " << std::setprecision(1) << accuracy * 100.0 << "%\n";
    print_boundary(model);
    return accuracy >= 0.85 ? 0 : 2;
}
