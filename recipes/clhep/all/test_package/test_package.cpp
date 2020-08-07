#include "CLHEP/Matrix/Matrix.h"

#include <CLHEP/Random/RandGauss.h>
#include <CLHEP/Random/RandGaussQ.h>
#include <CLHEP/Random/RandExponential.h>
#include <CLHEP/Random/RandGaussZiggurat.h>
#include <CLHEP/Random/RandExpZiggurat.h>

#include <iostream>

void check_matrix_component() {
  std::cout << "======================" << std::endl;
  std::cout << "Check Matrix component" << std::endl;
  std::cout << "======================" << std::endl;

  CLHEP::HepMatrix mtr(7, 7, 0);
  for (int i = 1; i < 8; ++i) {
    for (int j = 1; j < 8; ++j) {
      if (i <= j) {
        mtr(i, j) = 10 * i + j;
        mtr(j, i) = 10 * j + i;
      }
    }
  }

  std::cout << "Initial matrix " << mtr << std::endl;
  std::cout << "Sub (1,4,1,4)" << mtr.sub(1, 4, 1, 4) << std::endl;
}

void check_random_component() {
  std::cout << "======================" << std::endl;
  std::cout << "Check Random component" << std::endl;
  std::cout << "======================" << std::endl;

  int ntest = 10;

  std::cout << "DEBUG: ntest=" << ntest << std::endl;

  double sum_rnd1 = 0;
  for (int i = 0; i < ntest; ++i) {
    double g = CLHEP::RandGauss::shoot();
    sum_rnd1 += g;
  }
  sum_rnd1 /= ntest;
  std::cout << "DEBUG: avg RandGauss=" << sum_rnd1 << std::endl;

  double sum_rnd2 = 0;
  for (int i = 0; i < ntest; ++i) {
    double g = CLHEP::RandGaussQ::shoot();
    sum_rnd2 += g;
  }
  sum_rnd2 /= ntest;
  std::cout << "DEBUG: avg RandGaussQ=" << sum_rnd2 << std::endl;

  double sum_zig = 0;
  for(int i = 0; i < ntest; ++i) {
    double g = CLHEP::RandGaussZiggurat::shoot();
     sum_zig += g;
  }
  sum_zig /= ntest;
  std::cout << "DEBUG: avg RandGaussZiggurat=" << sum_zig << std::endl;

  double sum_exp = 0;
  for (int i = 0; i < ntest; ++i) {
    double g = CLHEP::RandExponential::shoot();
    sum_exp += g;
  }
  sum_exp /= ntest;
  std::cout << "DEBUG: avg RandExponential=" << sum_exp << std::endl;

  double sum_expZ = 0;
  for (int i = 0; i < ntest; ++i) {
    double g = CLHEP::RandExpZiggurat::shoot();
    sum_expZ += g;
  }
  sum_expZ /= ntest;
  std::cout << "DEBUG: avg RandExpZiggurat=" << sum_expZ << std::endl;
}

int main() {
  check_matrix_component();
  check_random_component();

  return 0;
}
