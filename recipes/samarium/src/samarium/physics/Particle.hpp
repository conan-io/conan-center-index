/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "../graphics/Color.hpp"
#include "../math/shapes.hpp"

namespace sm
{
struct Particle
{
    Vector2 pos{};
    Vector2 vel{};
    Vector2 acc{};
    f64 radius{1};
    f64 mass{1};
    Color color{};

    [[nodiscard]] Circle as_circle() const noexcept;

    void apply_force(Vector2 force) noexcept;

    void update(f64 time_delta = 1.0 / 64) noexcept;
};
} // namespace sm
