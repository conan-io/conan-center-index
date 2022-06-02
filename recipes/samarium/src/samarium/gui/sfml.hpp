/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "SFML/Graphics.hpp"
#include "SFML/Graphics/Color.hpp"
#include "SFML/Window.hpp"

#include "../graphics/Color.hpp"
#include "../math/Vector2.hpp"
#include <SFML/System/Vector2.hpp>

namespace sm
{
template <typename T> [[nodiscard]] constexpr Vector2_t<T> sfml(sf::Vector2<T> vec) noexcept
{
    return {vec.x, vec.y};
}
template <typename T> [[nodiscard]] constexpr sf::Vector2<T> sfml(Vector2_t<T> vec) noexcept
{
    return {vec.x, vec.y};
}

[[nodiscard]] inline auto sfml(Color color)
{
    return sf::Color{color.r, color.g, color.b, color.a};
}
} // namespace sm
