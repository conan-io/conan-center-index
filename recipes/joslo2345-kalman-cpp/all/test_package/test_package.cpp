#include <cstdio>

#include <kalman/kalman.hpp>

int main() {
    using KF = kalman::LinearFilter<2, 1>;
    KF::Transition F;
    F << 1, 0.1, 0, 1;
    KF::Observation H;
    H << 1, 0;
    KF kf(F, H, 1e-3 * KF::Cov::Identity(), KF::MeasCov::Constant(0.25), KF::State(0.0, 0.0),
          10.0 * KF::Cov::Identity());
    kf.predict();
    kf.update(KF::Measurement(1.0));
    std::printf("kalman-cpp %s: position %.3f\n", kalman::version, kf.state()(0));
    return 0;
}
