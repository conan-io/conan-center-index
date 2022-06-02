/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include <algorithm>
#include <ranges>

#include "../math/Extents.hpp"

#include "ParticleSystem.hpp"
#include "collision.hpp"

namespace sm
{
void ParticleSystem::update(f64 time_delta) noexcept
{
    std::for_each(particles.begin(), particles.end(),
                  [time_delta](Particle& particle) { particle.update(time_delta); });
}


void ParticleSystem::apply_force(Vector2 force) noexcept
{
    std::for_each(particles.begin(), particles.end(),
                  [force](Particle& particle) { particle.apply_force(force); });
}

void ParticleSystem::apply_forces(std::span<Vector2> forces) noexcept
{
    for (auto i : range(forces.size())) { particles[i].apply_force(forces[i]); }
}

void ParticleSystem::for_each(FunctionRef<void(Particle&)> function)
{
    std::ranges::for_each(particles, function);
}

void ParticleSystem::self_collision() noexcept
{
    for (auto i = particles.begin(); i != particles.end(); ++i)
    {
        for (auto j = particles.begin(); j != particles.end(); ++j)
        {
            if (i != j) { phys::collide(*i, *j); }
        }
    }
}
}; // namespace sm
