#include "neuroforge/value.hpp"

#include <cmath>
#include <iostream>
#include <string>

using neuroforge::Value;
int failures = 0;

void expect_near(double actual, double expected, double tolerance, const std::string& name) {
    if (std::abs(actual - expected) > tolerance) {
        std::cerr << "FAIL " << name << ": expected " << expected << ", got " << actual << '\n';
        ++failures;
    }
}

int main() {
    { Value x(3.0); Value y = x * x; y.backward();
      expect_near(y.data(), 9.0, 1e-12, "square value");
      expect_near(x.grad(), 6.0, 1e-12, "square derivative"); }
    { Value x(2.0); Value y = x * x + x; y.backward();
      expect_near(y.data(), 6.0, 1e-12, "shared graph value");
      expect_near(x.grad(), 5.0, 1e-12, "shared graph derivative"); }
    { Value x(0.4); Value y = x.tanh(); y.backward();
      expect_near(x.grad(), 1.0 - std::pow(std::tanh(0.4), 2.0), 1e-12, "tanh derivative"); }
    { Value x(-1.3); Value y = (x.exp() + 2.0).log(); y.backward();
      const double expected = std::exp(-1.3) / (std::exp(-1.3) + 2.0);
      expect_near(x.grad(), expected, 1e-12, "composed derivative"); }
    if (failures == 0) std::cout << "All autograd tests passed.\n";
    return failures == 0 ? 0 : 1;
}
