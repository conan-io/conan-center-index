// poncelet — Conan test_package smoke: register a type, spawn a shot, step
// it, print a one-line summary. Proves the packaged poncelet::poncelet
// target actually links and runs, not just that it compiles.
#include <poncelet/poncelet.hpp>

#include <cstdio>

int main() {
    pon::Sim sim;
    pon::ProjectileType t;
    t.id = "conan_test_9mm";
    t.klass = pon::ProjectileClass::Bullet;
    t.dragModel = pon::DragModel::ConstantCd;
    t.dragCoefficient = 0.30;
    t.mass_kg = 0.008;
    t.refDiameter_m = 0.009;
    t.muzzleSpeed_mps = 360.0;

    const pon::TypeId id = sim.registerType(t);
    if (id == pon::kInvalidType) {
        std::fprintf(stderr, "registerType failed: %s\n", sim.lastError());
        return 1;
    }

    pon::LaunchParams lp;
    lp.position = {0, 1.7, 0};
    lp.direction = {1, 0, 0};
    const pon::StateId h = sim.spawn(id, lp);

    pon::EmptyWorld world;
    pon::VectorEventSink sink;
    for (int i = 0; i < 60; ++i) sim.step(1.0 / 60.0, world, sink);

    std::printf("poncelet Conan test_package: %s\n", pon::describe(sim.state(h)).c_str());
    return 0;
}
