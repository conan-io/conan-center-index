#include <iostream>
#include <Eigen/Dense>
#include <eiquadprog/eiquadprog.hpp>

int main() {
    // Definition of the quadratic programming problem:
    // minimize 0.5 * x^T * G * x + g0^T * x
    // subject to: CE * x + ce0 = 0, CI * x + ci0 >= 0

    // Dimension of variable x
    int n = 2;

    // Matrix G (quadratic part of the objective function, must be positive definite)
    Eigen::MatrixXd G(2, 2);
    G << 2, 0,
         0, 2;

    // Vector g0 (linear part of the objective function)
    Eigen::VectorXd g0(2);
    g0 << -2, -5;

    // Equality constraints: CE * x + ce0 = 0
    Eigen::MatrixXd CE(2, 0); // No equality constraints in this example
    Eigen::VectorXd ce0(0);

    // Inequality constraints: CI * x + ci0 >= 0
    Eigen::MatrixXd CI(2, 3);
    CI << -1, 0, -1,  // -x1 >= -2  => x1 <= 2
          0, -1, -1;  // -x2 >= -2  => x2 <= 2
    Eigen::VectorXd ci0(3);
    ci0 << 2, 2, 0; // Corresponding constants

    // Vector to store the solution
    Eigen::VectorXd x(n);

    // Additional arguments for solve_quadprog
    Eigen::VectorXi active_set(CI.cols()); // Active set vector, size equals the number of inequalities
    size_t max_iter = 100; // Maximum number of iterations

    // Solving the quadratic programming problem
    double cost = eiquadprog::solvers::solve_quadprog(G, g0, CE, ce0, CI, ci0, x, active_set, max_iter);

    if (cost == std::numeric_limits<double>::infinity()) {
        std::cout << "The problem has no solution or is unbounded.\n";
    } else {
        std::cout << "Optimal solution found:\n";
        std::cout << "x = " << x.transpose() << "\n";
        std::cout << "Objective function value: " << cost << "\n";
    }

    return 0;
}
