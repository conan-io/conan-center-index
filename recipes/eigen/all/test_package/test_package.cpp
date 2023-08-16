#include <iostream>
#include <Eigen/Core>
#include <unsupported/Eigen/MatrixFunctions>


int main(void)
{
    int const N = 5;
    Eigen::MatrixXi A(N, N);
    A.setRandom();

    std::cout << "A =\n" << A << "\n\n"
              << "A(2..3,:) =\n" << A.middleRows(2, 2) << "\n";

    return 0;
}
