#include <iostream>
#include <armadillo>

int main() {
    std::cout << "Armadillo version: " << arma::arma_version::as_string() << std::endl;
    const arma::vec a = {1.0, 2.0, 3.0};
    const arma::vec b = {4.0, 5.0, 6.0};
    std::cout << "dot(a, b) = " << arma::dot(a, b) << std::endl;
    return 0;
}
