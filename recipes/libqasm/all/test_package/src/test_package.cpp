#include "cqasm.hpp"

#include <iostream>


int main() {
    auto analyzer = cqasm::v3x::default_analyzer();
    auto result = analyzer.analyze_string("version 3.0; qubit[2] q; H q[0]; CNOT q[0], q[1]; measure q", "");
    std::cout << result.to_json();
}
