/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "Car.hpp"

namespace sm
{
void Car::update(f64 delta)
{
    this->vel += this->acc * delta;
    const auto delta_vel = this->vel * delta;

    if (std::abs(this->turn_angle) < 0.01)
    {
        this->pos += Vector2::from_polar({.length = delta_vel, .angle = this->body_angle});
        return;
    }

    // const auto turning_radius = this->track / std::tan(this->turn_angle);
    // const auto sign           = math::sign(turning_radius);
    // print(turning_radius);
}
} // namespace sm
