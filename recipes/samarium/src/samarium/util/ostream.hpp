/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include <iostream>

#include "../util/format.hpp"

auto operator<<(std::ostream& os, const sm::Version& a) -> std::ostream&;

auto operator<<(std::ostream& os, const sm::Color& a) -> std::ostream&;

template <sm::concepts::Number T>
auto operator<<(std::ostream& os, const sm::BoundingBox<T>& a) -> std::ostream&
{
    os << fmt::format("{}", a);
    return os;
}

template <sm::concepts::Number T>
auto operator<<(std::ostream& os, const sm::Vector2_t<T>& a) -> std::ostream&
{
    os << fmt::format("{}", a);
    return os;
}
