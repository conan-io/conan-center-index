#include <cstdint>
#include <iostream>

#include "ruy/ruy.h"

int main() {

  ruy::Context context;
  const float lhs_data[] = {1, 2, 3, 4};
  const float rhs_data[] = {1, 2, 3, 4};
  float dst_data[4];

  ruy::Matrix<float> lhs;
  ruy::MakeSimpleLayout(2, 2, ruy::Order::kRowMajor, lhs.mutable_layout());
  lhs.set_data(lhs_data);
  ruy::Matrix<float> rhs;
  ruy::MakeSimpleLayout(2, 2, ruy::Order::kColMajor, rhs.mutable_layout());
  rhs.set_data(rhs_data);
  ruy::Matrix<float> dst;
  ruy::MakeSimpleLayout(2, 2, ruy::Order::kColMajor, dst.mutable_layout());
  dst.set_data(dst_data);

  ruy::MulParams<float, float> mul_params;
  ruy::Mul(lhs, rhs, mul_params, &context, &dst);

  std::cout << "ruy's test_package ran successfully \n";
}
