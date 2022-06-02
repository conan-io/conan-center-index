/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "Vector2.hpp"

namespace sm
{
struct Circle
{
    Vector2 centre{};
    f64 radius{};

    [[nodiscard]] constexpr auto at_angle(f64 angle) const noexcept
    {
        return centre + Vector2::from_polar({.length = radius, .angle = angle});
    }

    /* Assuming point is on Circle, move it counter-clockwise */
    [[nodiscard]] constexpr auto move_along(Vector2 point, f64 distance) const noexcept
    {
        return centre + (point - centre).rotated_by(distance / this->radius);
    }
};

struct LineSegment
{
    Vector2 p1{};
    Vector2 p2{};

    [[nodiscard]] constexpr auto vector() const noexcept { return p2 - p1; }

    [[nodiscard]] constexpr auto length() const noexcept { return vector().length(); }

    [[nodiscard]] constexpr auto length_sq() const noexcept { return vector().length_sq(); }

    [[nodiscard]] constexpr auto slope() const noexcept { return vector().slope(); }

    constexpr auto translate(Vector2 amount) noexcept
    {
        this->p1 += amount;
        this->p2 += amount;
    }
};

} // namespace sm
