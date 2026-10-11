#include <mexce.h>
#include <cmath>

int main() {
    double value = 2.0;
    mexce::evaluator eval;
    eval.bind(value, "value");
    eval.set_expression("value * value + 1");
    if (!(std::abs(eval.evaluate() - 5.0) < 1e-12)) {
        return 1;
    }
    value = 3.0;
    return std::abs(eval.evaluate() - 10.0) < 1e-12 ? 0 : 1;
}
