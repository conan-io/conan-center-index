/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "../math/vector_math.hpp"
#include "Particle.hpp"

namespace sm
{
struct Spring
{
    Particle& p1;
    Particle& p2;
    const f64 rest_length;
    const f64 stiffness;
    const f64 damping;

    Spring(Particle& particle1,
           Particle& particle2,
           f64 stiffness_ = 100.0,
           f64 damping_   = 10.0) noexcept
        : p1{particle1}, p2{particle2}, rest_length{math::distance(particle1.pos, particle2.pos)},
          stiffness{stiffness_}, damping{damping_}
    {
    }

    [[nodiscard]] auto length() const noexcept -> f64;

    void update() noexcept;
};
} // namespace sm
