#pragma once

#include "neuroforge/value.hpp"

#include <cmath>
#include <cstddef>
#include <random>
#include <stdexcept>
#include <utility>
#include <vector>

namespace neuroforge {

class Neuron {
public:
    Neuron(std::size_t inputs, std::mt19937& generator, bool nonlinear)
        : bias_(0.0), nonlinear_(nonlinear) {
        const double limit = std::sqrt(6.0 / static_cast<double>(inputs + 1));
        std::uniform_real_distribution<double> distribution(-limit, limit);
        weights_.reserve(inputs);
        for (std::size_t i = 0; i < inputs; ++i) weights_.emplace_back(distribution(generator));
    }

    Value operator()(const std::vector<Value>& inputs) const {
        if (inputs.size() != weights_.size()) throw std::invalid_argument("input size does not match neuron width");
        Value activation = bias_;
        for (std::size_t i = 0; i < inputs.size(); ++i) activation = activation + weights_[i] * inputs[i];
        return nonlinear_ ? activation.tanh() : activation;
    }

    std::vector<Value*> parameters() {
        std::vector<Value*> result;
        result.reserve(weights_.size() + 1);
        for (auto& weight : weights_) result.push_back(&weight);
        result.push_back(&bias_);
        return result;
    }

private:
    std::vector<Value> weights_;
    Value bias_;
    bool nonlinear_;
};

class Layer {
public:
    Layer(std::size_t inputs, std::size_t outputs, std::mt19937& generator, bool nonlinear) {
        neurons_.reserve(outputs);
        for (std::size_t i = 0; i < outputs; ++i) neurons_.emplace_back(inputs, generator, nonlinear);
    }

    std::vector<Value> operator()(const std::vector<Value>& inputs) const {
        std::vector<Value> outputs;
        outputs.reserve(neurons_.size());
        for (const auto& neuron : neurons_) outputs.push_back(neuron(inputs));
        return outputs;
    }

    std::vector<Value*> parameters() {
        std::vector<Value*> result;
        for (auto& neuron : neurons_) {
            auto current = neuron.parameters();
            result.insert(result.end(), current.begin(), current.end());
        }
        return result;
    }

private:
    std::vector<Neuron> neurons_;
};

class MLP {
public:
    MLP(std::size_t inputs, const std::vector<std::size_t>& widths, unsigned seed = 42) {
        if (widths.empty()) throw std::invalid_argument("an MLP needs at least one layer");
        std::mt19937 generator(seed);
        std::size_t previous = inputs;
        layers_.reserve(widths.size());
        for (std::size_t i = 0; i < widths.size(); ++i) {
            const bool nonlinear = i + 1 != widths.size();
            layers_.emplace_back(previous, widths[i], generator, nonlinear);
            previous = widths[i];
        }
    }

    std::vector<Value> operator()(std::vector<Value> inputs) const {
        for (const auto& layer : layers_) inputs = layer(inputs);
        return inputs;
    }

    Value scalar(const std::vector<double>& input) const {
        std::vector<Value> values;
        values.reserve(input.size());
        for (double item : input) values.emplace_back(item);
        const auto output = (*this)(std::move(values));
        if (output.size() != 1) throw std::logic_error("scalar() requires one output neuron");
        return output.front();
    }

    std::vector<Value*> parameters() {
        std::vector<Value*> result;
        for (auto& layer : layers_) {
            auto current = layer.parameters();
            result.insert(result.end(), current.begin(), current.end());
        }
        return result;
    }

private:
    std::vector<Layer> layers_;
};

class Adam {
public:
    Adam(std::vector<Value*> parameters, double learning_rate = 0.02,
         double beta1 = 0.9, double beta2 = 0.999, double epsilon = 1e-8)
        : parameters_(std::move(parameters)), first_moment_(parameters_.size(), 0.0),
          second_moment_(parameters_.size(), 0.0), learning_rate_(learning_rate),
          beta1_(beta1), beta2_(beta2), epsilon_(epsilon) {}

    void zero_grad() { for (auto* parameter : parameters_) parameter->zero_grad(); }

    void step() {
        ++step_;
        const double first_correction = 1.0 - std::pow(beta1_, static_cast<double>(step_));
        const double second_correction = 1.0 - std::pow(beta2_, static_cast<double>(step_));
        for (std::size_t i = 0; i < parameters_.size(); ++i) {
            const double gradient = parameters_[i]->grad();
            first_moment_[i] = beta1_ * first_moment_[i] + (1.0 - beta1_) * gradient;
            second_moment_[i] = beta2_ * second_moment_[i] + (1.0 - beta2_) * gradient * gradient;
            const double corrected_first = first_moment_[i] / first_correction;
            const double corrected_second = second_moment_[i] / second_correction;
            parameters_[i]->set_data(parameters_[i]->data() - learning_rate_ * corrected_first /
                                     (std::sqrt(corrected_second) + epsilon_));
        }
    }

private:
    std::vector<Value*> parameters_;
    std::vector<double> first_moment_;
    std::vector<double> second_moment_;
    double learning_rate_;
    double beta1_;
    double beta2_;
    double epsilon_;
    std::size_t step_{};
};

}  // namespace neuroforge
