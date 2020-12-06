#include <gtsam/geometry/Rot2.h>
#include <gtsam/inference/Symbol.h>
#include <gtsam/slam/PriorFactor.h>

using namespace gtsam;

const double degree = M_PI / 180;

int main() {

  Rot2 prior = Rot2::fromAngle(30 * degree);
  prior.print("30 degrees in radians is");
  noiseModel::Isotropic::shared_ptr model = noiseModel::Isotropic::Sigma(1, 1 * degree);
  Symbol key('x',1);
  PriorFactor<Rot2> factor(key, prior, model);

  return 0;
}
