#include <manif/manif.h>

using namespace manif;

int main() {
  SE3d X = SE3d::Random();
  SE3Tangentd w = SE3Tangentd::Random();
  SE3d::Jacobian J_o_x, J_o_w;
  auto X_plus_w = X.plus(w, J_o_x, J_o_w);
}
