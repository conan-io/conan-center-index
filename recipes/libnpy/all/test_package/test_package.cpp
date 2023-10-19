#include "npy.hpp"
#include <vector>
#include <string>

int main() {
  const std::vector<double> data{1, 2, 3, 4, 5, 6};

  npy::npy_data<double> d;
  d.data = data;
  d.shape = {2, 3};
  d.fortran_order = false;

  const std::string path{"out.npy"};
  npy::write_npy(path, d);
}
