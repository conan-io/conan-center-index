/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "../math/Dual.hpp"
#include "../math/Transform.hpp"

#include "sfml.hpp"

namespace sm
{
struct Mouse
{
    enum class Button
    {
        Left,
        Right
    };

    Dual<Vector2> pos;
    f64 scroll_amount{};
    bool left;
    bool middle;
    bool right;

    explicit Mouse(const sf::RenderWindow& window) { this->update(window); }

    void update(const sf::RenderWindow& window);

    [[nodiscard]] auto apply(Transform transform, Mouse::Button btn = Button::Left) const
        -> Transform;

    [[nodiscard]] auto vel() const -> Vector2;
};
} // namespace sm
