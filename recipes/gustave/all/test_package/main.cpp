
#include <gustave/distribs/std/strictUnit/Gustave.hpp>

using G = gustave::distribs::std::strictUnit::Gustave<double>;

static constexpr auto u = G::units();

static auto const blockDimensions = G::vector3(1.f, 1.f, 1.f, u.length);
static auto const gravity = G::vector3(0.f, -10.f, 0.f, u.acceleration);
static auto const solverPrecision = 0.001f;

G::Worlds::SyncWorld newWorld() {
    using Solver = G::Worlds::SyncWorld::Solver;
    auto solver = Solver{ Solver::Config{ gravity, solverPrecision } };
    return G::Worlds::SyncWorld{ blockDimensions, std::move(solver) };
}

int main() {
    auto const concrete_20m = G::Worlds::SyncWorld::BlockReference::PressureStress{
        20'000'000.f * u.pressure, // max compressive pressure
        14'000'000.f * u.pressure, // max shear pressure
        2'000'000.f * u.pressure, // max tensile pressure
    };
    auto const blockMass = 2'400.f * u.mass;

    auto world = newWorld();
    {
        auto transaction = G::Worlds::SyncWorld::Transaction{};
        transaction.addBlock({ {0,1,0}, concrete_20m, blockMass, false });
        transaction.addBlock({ {0,0,0}, concrete_20m, blockMass, true });
        world.modify(transaction);
    }

    auto const contactIndex = G::Worlds::SyncWorld::ContactIndex{ {0,0,0}, G::Worlds::SyncWorld::ContactIndex::Direction::plusY() };
    auto const contactForce = world.contacts().at(contactIndex).forceVector();
    auto const expectedForce = blockMass * gravity;

    if ((contactForce - expectedForce).norm() <= solverPrecision * expectedForce.norm()) {
        return 0;
    } else {
        return 1;
    }
}
