#include <TooN/TooN.h>
#include <TooN/determinant.h>

#ifdef USE_LAPACK
#include <TooN/Lapack_Cholesky.h>
#endif

#include <iostream>
#include <iomanip>

using namespace TooN;

void test_determinant() {
    Matrix<3> t = Data(
         1,   0.5, 0.5,
         0.5,   2, 0.7,
         0.5, 0.7,   3);
    std::cout << "determinant: " << determinant(t) << std::endl;
}

#ifdef USE_LAPACK
void test_lapack() {
  Matrix<3> t = Data(
      1,   0.5, 0.5,
      0.5,   2, 0.7,
      0.5, 0.7,   3);
  Lapack_Cholesky<3> chol(t);
  std::cout << "Lapack_Cholesky determinat: " << chol.determinant() << std::endl;
}
#endif

int main() {
  test_determinant();

#ifdef USE_LAPACK
  test_lapack();
#endif
}
