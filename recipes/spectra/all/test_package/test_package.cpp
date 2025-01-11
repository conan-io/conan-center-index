#include <Eigen/Core>
#include <Spectra/SymEigsSolver.h>

int main() {
    Eigen::MatrixXd A = Eigen::MatrixXd::Random(10, 10);
    Spectra::DenseSymMatProd<double> op(A);
}
