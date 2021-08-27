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
#ifdef SPECTRA_LESS_1_0_0
    Spectra::SymEigsSolver< double, Spectra::LARGEST_ALGE, Spectra::DenseSymMatProd<double> > eigs(&op, 3, 6);
#else
    Spectra::SymEigsSolver<Spectra::DenseSymMatProd<double>> eigs(op, 3, 6);
#endif

    // Initialize and compute
    eigs.init();
#ifdef SPECTRA_LESS_1_0_0
    int nconv = eigs.compute();
#else
    int nconv = eigs.compute(Spectra::SortRule::LargestAlge);
#endif

    // Retrieve results
    Eigen::VectorXd evalues;
#ifdef SPECTRA_LESS_1_0_0
    if (eigs.info() == Spectra::SUCCESSFUL) {
#else
    if (eigs.info() == Spectra::CompInfo::Successful) {
#endif
        evalues = eigs.eigenvalues();
    }

    std::cout << "Eigenvalues found:\n" << evalues << std::endl;

    return 0;
}
