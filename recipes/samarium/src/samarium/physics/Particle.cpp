/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "Particle.hpp"

namespace sm
{
[[nodiscard]] Circle Particle::as_circle() const noexcept { return Circle{pos, radius}; }

void Particle::apply_force(Vector2 force) noexcept { acc += force / mass; }

void Particle::update(f64 time_delta) noexcept
{
    vel += acc * time_delta;
    pos += vel * time_delta;
    acc = Vector2{}; // reset acceleration
}
}; // namespace sm
