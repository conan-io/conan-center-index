/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <array>

#include "../math/interp.hpp"
#include "../util/print.hpp"

#include "Color.hpp"

namespace sm
{
template <size_t size> class Gradient
{
    std::array<Color, size> colors;

  public:
    explicit constexpr Gradient(auto&&... colors_) : colors{colors_...} {}

    [[nodiscard]] auto operator()(f64 factor) const
    {
        const auto mapped = factor * (size - 1UL) + 0.01;
        // TODO the +0.1 prevents the map range from dividing by 0

        const auto lower = static_cast<size_t>(mapped);            // static_cast rounds down
        const auto upper = static_cast<size_t>(std::ceil(mapped)); // round up
        const auto mapped_factor =
            interp::map_range<f64>(mapped, {std::floor(mapped), std::ceil(mapped)}, {0.0, 1.0});

        return interp::lerp_rgb(mapped_factor, colors[lower], colors[upper]);
    }
};

template <typename... Args> Gradient(Args... args) -> Gradient<sizeof...(Args)>;

template <> class Gradient<2>
{
    Color from{};
    Color to{};

  public:
    explicit constexpr Gradient(Color from_, Color to_) : from{from_}, to{to_} {}

    constexpr auto operator()(f64 factor) const { return interp::lerp_rgb(factor, from, to); }
};

template <> class Gradient<3>
{
    Color from{};
    Color mid{};
    Color to{};

  public:
    explicit constexpr Gradient(Color from_, Color mid_, Color to_)
        : from{from_}, mid{mid_}, to{to_}
    {
    }

    constexpr auto operator()(f64 factor) const
    {
        factor = Extents<f64>{0.0, 1.0}.clamp(factor);
        if (factor < 0.5) { return interp::lerp_rgb(2.0 * factor, from, mid); }
        else
        {
            return interp::lerp_rgb(2.0 * (factor - 0.5), mid, to);
        }
    }
};
} // namespace sm
