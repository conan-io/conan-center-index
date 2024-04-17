#include <TooN/Lapack_Cholesky.h>

#include <iostream>
#include <iomanip>

using namespace TooN;

int main() {
    Matrix<3> t = Data(
         1,   0.5, 0.5,
         0.5,   2, 0.7,
         0.5, 0.7,   3);
    Lapack_Cholesky<3> chol(t);
    std::cout << chol.determinant() << std::endl;
}
