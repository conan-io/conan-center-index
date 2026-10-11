#include <mexce_protected_encoder.h>
#include <cmath>
#include <utility>

int main() {
    double value = 2.0;
    mexce::evaluator eval;
    eval.bind_protected(value, 0);
    auto bundle = mexce::encode_protected_expression(
        "value * value + 1", {{"value", 0}}, mexce::Protected_math_mode::STRICT);
    eval.set_protected_expression(
        bundle.program.data(), bundle.program.size(), std::move(bundle.key));
    if (!(std::abs(eval.evaluate() - 5.0) < 1e-12)) {
        return 1;
    }
    value = 3.0;
    return std::abs(eval.evaluate() - 10.0) < 1e-12 ? 0 : 1;
}
