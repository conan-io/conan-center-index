// This test is not representative of all the library capabilities.
// It is extracted from the example 002[1] of the tutorial
//
// [1] https://github.com/libigl/libigl/blob/master/tutorial/202_GaussianCurvature/main.cpp
#include <igl/gaussian_curvature.h>
#include <igl/massmatrix.h>
#include <igl/invert_diag.h>
#include <igl/readOFF.h>

int main()
{
    using namespace Eigen;
    MatrixXd V(3, 3);

    V << 0, 0, 0,
        1, 1, 0,
        -1, 1, 0;

    MatrixXi F(1, 3);
    F << 0, 1, 2;

    // Compute integral of Gaussian curvature
    VectorXd K;
    igl::gaussian_curvature(V, F, K);

    // Compute mass matrix
    SparseMatrix<double> M, Minv;
    igl::massmatrix(V, F, igl::MASSMATRIX_TYPE_DEFAULT, M);

    igl::invert_diag(M, Minv);
}
