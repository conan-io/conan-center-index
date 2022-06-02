/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "fmt/color.h"

#include "../core/version.hpp"
#include "../graphics/Color.hpp"
#include "../math/BoundingBox.hpp"
#include "../math/Transform.hpp"
#include "../math/Vector2.hpp"
#include "../math/complex.hpp"
#include "../math/shapes.hpp"
#include "../physics/Particle.hpp"

namespace fmt
{
template <sm::concepts::Number T> class formatter<sm::Vector2_t<T>>
{
  public:
    constexpr auto parse(const format_parse_context& ctx) { return ctx.begin(); }

    constexpr auto format(sm::Vector2_t<T> p, auto& ctx)
    {
        return fmt::format_to(ctx.out(),
                              (sm::concepts::FloatingPoint<T>
                                   ? "\033[1mVec\033[0m({: 6.3f}, {: 6.3f})"
                                   : "Vec({:>3}, {:>3})"),
                              p.x, p.y);
    }
};

template <> class formatter<sm::Version>
{
  public:
    constexpr auto parse(const format_parse_context& ctx) { return ctx.begin(); }

    auto format(const sm::Version& p, auto& ctx)
    {
        return fmt::format_to(ctx.out(), "samarium version {}.{}.{}", p.major, p.minor, p.patch);
    }
};

template <> class formatter<sm::Particle>
{
  public:
    constexpr auto parse(const format_parse_context& ctx) { return ctx.begin(); }

    auto format(const sm::Particle& p, auto& ctx)
    {
        return fmt::format_to(ctx.out(), "Particle(pos: {}, vel: {}, acc: {})", p.pos, p.acc,
                              p.vel);
    }
};

template <> class formatter<sm::Color>
{
  public:
    constexpr auto parse(const format_parse_context& ctx) const { return ctx.begin(); }

    auto format(const sm::Color& p, auto& ctx)
    {
        return fmt::format_to(ctx.out(),
                              "\x1b[38;2;{0};{1};{2}mCol\x1b[0m[{0:>3}, {1:>3}, {2:>3}, {3:>3}]",
                              p.r, p.g, p.b, p.a);
    }
};


template <sm::concepts::Number T> class formatter<sm::BoundingBox<T>>
{
  public:
    constexpr auto parse(const format_parse_context& ctx) { return ctx.begin(); }

    auto format(const sm::BoundingBox<T>& p, auto& ctx)
    {
        return fmt::format_to(ctx.out(),
                              R"(
BoundingBox(min = {},
            max = {}))",
                              p.min, p.max);
    }
};

template <> class formatter<sm::LineSegment>
{
  public:
    constexpr auto parse(const format_parse_context& ctx) const { return ctx.begin(); }

    auto format(const sm::LineSegment& p, auto& ctx)
    {
        return fmt::format_to(ctx.out(), "LineSegment({}, {})", p.p1, p.p2);
    }
};

template <> class formatter<sm::Transform>
{
  public:
    constexpr auto parse(const format_parse_context& ctx) const { return ctx.begin(); }

    auto format(const sm::Transform& p, auto& ctx)
    {
        return fmt::format_to(ctx.out(), "Transform[pos: {}, scale: {}]", p.pos, p.scale);
    }
};

template <> class formatter<std::complex<sm::f64>>
{
  public:
    constexpr auto parse(const format_parse_context& ctx) const { return ctx.begin(); }

    auto format(const std::complex<sm::f64>& p, auto& ctx)
    {
        return fmt::format_to(ctx.out(), "complex({:.4}, {:.4})", p.real(), p.imag());
    }
};
} // namespace fmt
