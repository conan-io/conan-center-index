#include <mexce.h>
#include <iostream>

int main() {
    mexce::evaluator eval;
    double x = 0.5;
    eval.bind(x, "x");
    eval.set_expression("sin(x) + 1");
    const double result = eval.evaluate();
    std::cout << "Result: " << result << '\n';
    return (result != 0.0) ? 0 : 1;
}
