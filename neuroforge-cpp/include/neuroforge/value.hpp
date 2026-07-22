#pragma once

#include <algorithm>
#include <atomic>
#include <cmath>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

namespace neuroforge {

class Value {
public:
    struct Node {
        double data{};
        double grad{};
        std::vector<std::shared_ptr<Node>> previous;
        std::function<void()> local_backward = [] {};
        std::string operation;
        std::size_t id{};
    };

    Value() : Value(0.0) {}
    explicit Value(double data) : node_(std::make_shared<Node>()) {
        node_->data = data;
        node_->id = next_id_++;
    }

    double data() const { return node_->data; }
    double grad() const { return node_->grad; }
    void set_data(double value) { node_->data = value; }
    void zero_grad() { node_->grad = 0.0; }

    void backward() {
        std::vector<std::shared_ptr<Node>> topology;
        std::unordered_set<std::size_t> visited;
        build_topology(node_, visited, topology);
        for (const auto& current : topology) current->grad = 0.0;
        node_->grad = 1.0;
        for (auto it = topology.rbegin(); it != topology.rend(); ++it) (*it)->local_backward();
    }

    Value operator+(const Value& other) const {
        auto out = make_node(data() + other.data(), {node_, other.node_}, "+");
        std::weak_ptr<Node> weak_out = out.node_;
        auto left = node_; auto right = other.node_;
        out.node_->local_backward = [weak_out, left, right] {
            if (const auto current = weak_out.lock()) {
                left->grad += current->grad;
                right->grad += current->grad;
            }
        };
        return out;
    }

    Value operator-(const Value& other) const { return *this + (-other); }

    Value operator-() const {
        auto out = make_node(-data(), {node_}, "neg");
        std::weak_ptr<Node> weak_out = out.node_;
        auto input = node_;
        out.node_->local_backward = [weak_out, input] {
            if (const auto current = weak_out.lock()) input->grad -= current->grad;
        };
        return out;
    }

    Value operator*(const Value& other) const {
        auto out = make_node(data() * other.data(), {node_, other.node_}, "*");
        std::weak_ptr<Node> weak_out = out.node_;
        auto left = node_; auto right = other.node_;
        out.node_->local_backward = [weak_out, left, right] {
            if (const auto current = weak_out.lock()) {
                left->grad += right->data * current->grad;
                right->grad += left->data * current->grad;
            }
        };
        return out;
    }

    Value operator/(const Value& other) const { return *this * other.pow(-1.0); }

    Value pow(double exponent) const {
        if (data() == 0.0 && exponent < 1.0) throw std::domain_error("invalid power at zero");
        auto out = make_node(std::pow(data(), exponent), {node_}, "pow");
        std::weak_ptr<Node> weak_out = out.node_;
        auto input = node_;
        out.node_->local_backward = [weak_out, input, exponent] {
            if (const auto current = weak_out.lock()) {
                input->grad += exponent * std::pow(input->data, exponent - 1.0) * current->grad;
            }
        };
        return out;
    }

    Value exp() const {
        auto out = make_node(std::exp(data()), {node_}, "exp");
        std::weak_ptr<Node> weak_out = out.node_;
        auto input = node_;
        out.node_->local_backward = [weak_out, input] {
            if (const auto current = weak_out.lock()) input->grad += current->data * current->grad;
        };
        return out;
    }

    Value log() const {
        if (data() <= 0.0) throw std::domain_error("log requires a positive value");
        auto out = make_node(std::log(data()), {node_}, "log");
        std::weak_ptr<Node> weak_out = out.node_;
        auto input = node_;
        out.node_->local_backward = [weak_out, input] {
            if (const auto current = weak_out.lock()) input->grad += current->grad / input->data;
        };
        return out;
    }

    Value tanh() const {
        const double result = std::tanh(data());
        auto out = make_node(result, {node_}, "tanh");
        std::weak_ptr<Node> weak_out = out.node_;
        auto input = node_;
        out.node_->local_backward = [weak_out, input, result] {
            if (const auto current = weak_out.lock()) input->grad += (1.0 - result * result) * current->grad;
        };
        return out;
    }

    Value relu() const {
        const double result = std::max(0.0, data());
        auto out = make_node(result, {node_}, "relu");
        std::weak_ptr<Node> weak_out = out.node_;
        auto input = node_;
        out.node_->local_backward = [weak_out, input] {
            if (const auto current = weak_out.lock()) input->grad += (input->data > 0.0 ? 1.0 : 0.0) * current->grad;
        };
        return out;
    }

    Value sigmoid() const {
        if (data() >= 0.0) return Value(1.0) / (Value(1.0) + (-(*this)).exp());
        const Value e = exp();
        return e / (Value(1.0) + e);
    }

private:
    std::shared_ptr<Node> node_;
    inline static std::atomic<std::size_t> next_id_{1};

    explicit Value(std::shared_ptr<Node> node) : node_(std::move(node)) {}

    static Value make_node(double data, std::vector<std::shared_ptr<Node>> previous, std::string operation) {
        auto node = std::make_shared<Node>();
        node->data = data;
        node->previous = std::move(previous);
        node->operation = std::move(operation);
        node->id = next_id_++;
        return Value(std::move(node));
    }

    static void build_topology(const std::shared_ptr<Node>& current,
                               std::unordered_set<std::size_t>& visited,
                               std::vector<std::shared_ptr<Node>>& topology) {
        if (!visited.insert(current->id).second) return;
        for (const auto& parent : current->previous) build_topology(parent, visited, topology);
        topology.push_back(current);
    }
};

inline Value operator+(double left, const Value& right) { return Value(left) + right; }
inline Value operator+(const Value& left, double right) { return left + Value(right); }
inline Value operator-(double left, const Value& right) { return Value(left) - right; }
inline Value operator-(const Value& left, double right) { return left - Value(right); }
inline Value operator*(double left, const Value& right) { return Value(left) * right; }
inline Value operator*(const Value& left, double right) { return left * Value(right); }
inline Value operator/(double left, const Value& right) { return Value(left) / right; }
inline Value operator/(const Value& left, double right) { return left / Value(right); }

}  // namespace neuroforge
