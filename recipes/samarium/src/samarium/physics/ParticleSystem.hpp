/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <span>
#include <vector>

#include "../util/FunctionRef.hpp"

#include "Particle.hpp"

namespace sm
{
struct ParticleSystem
{
    std::vector<Particle> particles;

    ParticleSystem(u64 size = 100UL, const Particle& default_particle = {})
        : particles(size, default_particle)
    {
    }

    void update(f64 time_delta = 1.0) noexcept;

    void apply_force(Vector2 force) noexcept;
    void apply_forces(std::span<Vector2> forces) noexcept;

    void for_each(FunctionRef<void(Particle&)> function);

    void self_collision() noexcept;

    auto operator[](u64 index) noexcept { return particles[index]; }
    auto operator[](u64 index) const noexcept { return particles[index]; }

    auto begin() noexcept { return particles.begin(); }
    auto end() noexcept { return particles.end(); }

    auto begin() const noexcept { return particles.cbegin(); }
    auto end() const noexcept { return particles.cend(); }

    auto cbegin() const noexcept { return particles.cbegin(); }
    auto cend() const noexcept { return particles.cend(); }

    auto size() const noexcept { return particles.size(); }
    auto empty() const noexcept { return particles.empty(); }
};
} // namespace sm
