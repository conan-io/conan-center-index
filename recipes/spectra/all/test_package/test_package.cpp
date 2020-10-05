#include <Eigen/Core>
#include <Spectra/SymEigsSolver.h>

#include <iostream>

int main() {
  // We are going to calculate the eigenvalues of M
  Eigen::MatrixXd A = Eigen::MatrixXd::Random(10, 10);
  Eigen::MatrixXd M = A + A.transpose();

  // Construct matrix operation object using the wrapper class DenseSymMatProd
  Spectra::DenseSymMatProd<double> op(M);

  // Construct eigen solver object, requesting the largest three eigenvalues
  Spectra::SymEigsSolver< double, Spectra::LARGEST_ALGE, Spectra::DenseSymMatProd<double> > eigs(&op, 3, 6);

  // Initialize and compute
  eigs.init();
  int nconv = eigs.compute();

  // Retrieve results
  Eigen::VectorXd evalues;
  if (eigs.info() == Spectra::SUCCESSFUL) {
    evalues = eigs.eigenvalues();
  }

  std::cout << "Eigenvalues found:\n" << evalues << std::endl;

  return 0;
}
