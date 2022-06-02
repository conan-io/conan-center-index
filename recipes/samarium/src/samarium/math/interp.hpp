/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "../graphics/Color.hpp"
#include "../math/Vector2.hpp"

#include "Extents.hpp"

namespace sm::interp
{
/**
 * @brief               Sigmoid-like smoothing
 * @param  value        Input value in the range [0, 1]
 */
[[nodiscard]] constexpr auto smooth_step(f64 value) { return value * value * (3.0 - 2.0 * value); }

/**
 * @brief               Smooth step but more!
 * @param  value        Input value in the range [0, 1]
 */
[[nodiscard]] constexpr auto smoother_step(f64 value)
{
    return value * value * value * (value * (value * 6.0 - 15.0) + 10.0);
}

// credit: https://gist.github.com/Bleuje/0917441d809d5eccf4ddcfc6a5b787d9

/**
 * @brief               Smooth a value with arbitrary smoothing
 *
 * @param  value        Input value in the range [0, 1]
 * @param  factor       Strength of smoothing: 1.0 is linear, higher values are smoother, values in
 * [0, 1) are inverse smoothing
 */
[[nodiscard]] inline auto ease(f64 value, f64 factor = 2.0)
{
    if (value < 0.5) { return 0.5 * std::pow(2.0 * value, factor); }
    else
    {
        return 1.0 - 0.5 * std::pow(2.0 * (1.0 - value), factor);
    }
}

/**
 * @brief               Ease In Sine
 * @param  value        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_in_sine(f64 value) { return 1.0 - std::cos(value * math::pi / 2.0); }

/**
 * @brief               Ease Out Sine
 * @param  value        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_out_sine(f64 value) { return std::sin(value * math::pi / 2.0); }

/**
 * @brief               Ease In Out Sine
 * @param  value        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_sine(f64 value) { return -(std::cos(math::pi * value) - 1.0) / 2.0; }

/**
 * @brief               Ease In Quad
 * @param  value        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_in_quad(f64 value) { return value * value; }

/**
 * @brief               Ease Out Quad
 * @param  value        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_out_quad(f64 value) { return 1.0 - (1.0 - value) * (1.0 - value); }

/**
 * @brief               Ease In Out Quad
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_quad(f64 x)
{
    return x < 0.5 ? 2.0 * x * x : 1.0 - std::pow(-2.0 * x + 2.0, 2.0) / 2.0;
}

/**
 * @brief               Ease In Cubic
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_in_cubic(f64 x) { return x * x * x; }

/**
 * @brief               Ease Out Cubic
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_out_cubic(f64 x) { return 1.0 - std::pow(1.0 - x, 3.0); }

/**
 * @brief               Ease In Out Cubic
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_cubic(f64 x)
{
    return x < 0.5 ? 4.0 * x * x * x : 1.0 - std::pow(-2.0 * x + 2.0, 3.0) / 2.0;
}

/**
 * @brief               Ease In Quart
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_in_quart(f64 x) { return x * x * x * x; }

/**
 * @brief               Ease Out Quart
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_out_quart(f64 x) { return 1.0 - std::pow(1.0 - x, 4.0); }

/**
 * @brief               Ease In Out Quart
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_quart(f64 x)
{
    return x < 0.5 ? 8.0 * x * x * x * x : 1.0 - pow(-2.0 * x + 2.0, 4.0) / 2.0;
}

/**
 * @brief               Ease In Quint
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_in_quint(f64 x) { return x * x * x * x * x; }

/**
 * @brief               Ease Out Quint
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_out_quint(f64 x) { return 1.0 - std::pow(1.0 - x, 5.0); }

/**
 * @brief               Ease In Out Quint
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_quint(f64 x) { return x * x * x * x * x; }

/**
 * @brief               Ease In Expo
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_in_expo(f64 x)
{
    return x == 0.0 ? 0.0 : std::pow(2.0, 10.0 * x - 10.0);
}

/**
 * @brief               Ease Out Expo
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_out_expo(f64 x)
{
    return x == 1.0 ? 1.0 : 1.0 - std::pow(2.0, -10.0 * x);
}

/**
 * @brief               Ease In Out Expo
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_expo(f64 x)
{
    return x < 0.5 ? std::pow(2.0, 20.0 * x - 10.0) / 2.0
                   : (2.0 - std::pow(2.0, -20.0 * x + 10.0)) / 2.0;
}

/**
 * @brief               Ease In Circ
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_in_circ(f64 x) { return 1.0 - std::sqrt(1.0 - std::pow(x, 2.0)); }

/**
 * @brief               Ease Out Circ
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_out_circ(f64 x) { return std::sqrt(1 - std::pow(x - 1, 2)); }

/**
 * @brief               Ease In Out Circ
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_circ(f64 x)
{
    return x < 0.5 ? (1.0 - std::sqrt(1.0 - std::pow(2.0 * x, 2.0))) / 2.0
                   : (std::sqrt(1.0 - std::pow(-2.0 * x + 2.0, 2.0)) + 1.0) / 2.0;
}

/**
 * @brief               Ease Out Back
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_in_back(f64 x) { return 2.70158 * x * x * x - 1.70158 * x * x; }

/**
 * @brief               Ease Out Back
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_out_back(f64 x)
{
    return 1.0 + 2.70158 * std::pow(x - 1.0, 3.0) + 1.70158 * std::pow(x - 1.0, 2.0);
}

/**
 * @brief               Ease In Out Back
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_back(f64 x)
{
    constexpr auto c1 = 1.70158;
    constexpr auto c2 = c1 * 1.525;

    return x < 0.5
               ? (std::pow(2.0 * x, 2.0) * ((c2 + 1.0) * 2.0 * x - c2)) / 2.0
               : (std::pow(2.0 * x - 2.0, 2.0) * ((c2 + 1.0) * (x * 2.0 - 2.0) + c2) + 2.0) / 2.0;
}

/**
 * @brief               Ease In Elastic
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_in_elastic(f64 x)
{
    return x == 0.0   ? 0.0
           : x == 1.0 ? 1.0
                      : -std::pow(2.0, 10.0 * x - 10.0) *
                            std::sin((x * 10.0 - 10.75) * math::two_thirds_pi);
}

/**
 * @brief               Ease Out Elastic
 * @param  value        Input value in the range [0, 1]
 * From https://easings.net/#easeOutElastic
 */
[[nodiscard]] constexpr auto ease_out_elastic(f64 value)
{
    if (value == 0.0) { return 0.0; }
    else if (value == 1.0)
    {
        return 1.0;
    }
    else
    {
        return std::pow(2.0, -10.0 * value) * std::sin((value * 10 - 0.75) * math::two_thirds_pi) +
               1;
    }
}

/**
 * @brief               Ease In Out Elastic
 * @param  x        Input value in the range [0, 1]
 */
[[nodiscard]] inline auto ease_elastic(f64 x)
{
    constexpr auto c5 = (2.0 * math::pi) / 4.5;

    return x == 0.0   ? 0.0
           : x == 1.0 ? 1.0
           : x < 0.5  ? -(pow(2.0, 20.0 * x - 10.0) * sin((20.0 * x - 11.125) * c5)) / 2
                      : (pow(2.0, -20.0 * x + 10.0) * sin((20.0 * x - 11.125) * c5)) / 2 + 1;
}

// TODO: Unsequenced modification
// /**
//  * @brief               Ease Out Bounce
//  * @param  x        Input value in the range [0, 1]
//  */
// [[nodiscard]] inline auto ease_out_bounce(f64 x)
// {
//     constexpr auto n1 = 7.5625;
//     constexpr auto d1 = 2.75;

//     if (x < 1.0 / d1) { return n1 * x * x; }
//     else if (x < 2.0 / d1)
//     {
//         return n1 * (x -= 1.5 / d1) * x + 0.75;
//     }
//     else if (x < 2.5 / d1)
//     {
//         return n1 * (x -= 2.25 / d1) * x + 0.9375;
//     }
//     else
//     {
//         return n1 * (x -= 2.625 / d1) * x + 0.984375;
//     }
// }

// /**
//  * @brief               Ease In Bounce
//  * @param  x        Input value in the range [0, 1]
//  */
// [[nodiscard]] inline auto ease_in_bounce(f64 x) { return 1.0 - ease_out_bounce(1.0 - x); }

// /**
//  * @brief               Ease In Out Bounce
//  * @param  x        Input value in the range [0, 1]
//  */
// [[nodiscard]] inline auto ease_bounce(f64 x)
// {
//     return x < 0.5 ? (1.0 - ease_out_bounce(1.0 - 2.0 * x)) / 2.0
//                    : (1.0 + ease_out_bounce(2.0 * x - 1.0)) / 2.0;
// }

/**
 * @brief               Check if a value is within asome Extents
 *
 * @param  value        Input value
 * @param  range_       Input range
 */
template <typename T> [[nodiscard]] constexpr auto in_range(T value, Extents<T> range_)
{
    return range_.contains(value);
}

/**
 * @brief               Ensure a value is within some Extents
 *
 * @param  value
 * @param  range_
 */
template <typename T> [[nodiscard]] constexpr auto clamp(T value, Extents<T> range_) noexcept
{
    return range_.clamp(value);
}

/**
 * @brief               Linearly interpolate a factor in a range
 * @param  factor
 * @param  range_
 */
template <typename T> [[nodiscard]] constexpr auto lerp(f64 factor, Extents<T> range_)
{
    return range_.lerp(factor);
}

/**
 * @brief               Lerp, but clamp the factor in [0, 1]
 * @param  factor
 * @param  range_
 */
template <typename T> [[nodiscard]] constexpr auto clamped_lerp(f64 factor, Extents<T> range_)
{
    return range_.clamped_lerp(factor);
}

/**
 * @brief               Lerp between the RGBA values of 2 Colors
 * @param  factor
 * @param  from
 * @param  to
 */
[[nodiscard]] constexpr auto lerp_rgb(f64 factor, Color from, Color to)
{
    return Color{static_cast<u8>(
                     lerp(factor, Extents<f64>{static_cast<f64>(from.r), static_cast<f64>(to.r)})),
                 static_cast<u8>(
                     lerp(factor, Extents<f64>{static_cast<f64>(from.g), static_cast<f64>(to.g)})),
                 static_cast<u8>(
                     lerp(factor, Extents<f64>{static_cast<f64>(from.b), static_cast<f64>(to.b)})),
                 static_cast<u8>(
                     lerp(factor, Extents<f64>{static_cast<f64>(from.a), static_cast<f64>(to.a)}))};
}

/**
 * @brief               Lerp between 2 vectors by rotating around a center
 * @param  from
 * @param  to
 * @param  center
 * @param  factor
 */
[[nodiscard]] constexpr auto lerp_rotate(Vector2 from, Vector2 to, Vector2 center, f64 factor)
{
    const auto radius = lerp<f64>(factor, {(from - center).length(), (to - center).length()});
    const auto angle  = lerp<f64>(factor, {from.angle(), to.angle()});
    return center + Vector2::from_polar({radius, angle});
}

/**
 * @brief               Clamped Lerp between 2 vectors by rotating around a center
 * @param  from
 * @param  to
 * @param  center
 * @param  factor
 */
[[nodiscard]] constexpr auto
clamped_lerp_rotate(Vector2 from, Vector2 to, Vector2 center, f64 factor)
{
    factor            = clamp(factor, {0.0, 1.0});
    const auto radius = lerp<f64>(factor, {(from - center).length(), (to - center).length()});
    const auto angle  = lerp<f64>(factor, {from.angle(), to.angle()});
    return center + Vector2::from_polar({radius, angle});
}

/**
 * @brief               Find the factor which lerps the value in the range
 * @param  value
 * @param  range_
 */
template <typename T> [[nodiscard]] constexpr auto lerp_inverse(f64 value, Extents<T> range_)
{
    return range_.lerp_inverse(value);
}

// https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another

/**
 * @brief               Map a value from an input range to an output range
 * @tparam T            Type of value
 * @tparam Output       Cast the result to Output
 * @param  value
 * @param  from
 * @param  to
 */
template <typename T, typename Output = T>
[[nodiscard]] constexpr auto map_range(T value, Extents<T> from, Extents<Output> to)
{
    return static_cast<Output>(to.min + (value - from.min) * to.size() / from.size());
}

/**
 * @brief               Map range, but clamp the value to the output range
 * @tparam T            Type of value
 * @tparam Output       Cast the result to Output
 * @param  value
 * @param  from
 * @param  to
 */
template <typename T, typename Output = T>
[[nodiscard]] constexpr auto map_range_clamp(T value, Extents<T> from, Extents<Output> to)
{
    return static_cast<Output>(to.min + (from.clamp(value) - from.min) * to.size() / from.size());
}

/**
 * @brief               Make a lambda which maps its argument from and to fixed ranges
 * @tparam T            Type of value
 * @tparam Output       Cast the result to Output
 * @param  from
 * @param  to
 */
template <typename T, typename Output = T>
[[nodiscard]] constexpr auto make_mapper(Extents<T> from, Extents<Output> to)
{
    return [from_min = from.min, from_range = from.size(), to_range = to.size(),
            to_min = to.min](T value)
    { return static_cast<Output>(to_min + (value - from_min) * to_range / from_range); };
}

/**
 * @brief               Make a lambda which maps its argument from and to fixed ranges, with
 * clamping
 * @tparam T            Type of value
 * @tparam Output       Cast the result to Output
 * @param  from
 * @param  to
 */
template <typename T, typename Output = T>
[[nodiscard]] constexpr auto make_clamped_mapper(Extents<T> from, Extents<Output> to)
{
    return [from, from_min = from.min, from_max = from.max, from_range = from.max - from.min,
            to_range = to.size(), to_min = to.min](T value) {
        return static_cast<Output>(to_min + (from.clamp(value) - from_min) * to_range / from_range);
    };
}

} // namespace sm::interp

namespace sm::concepts
{
/**
 * @brief               Can T be called with an f64 (commonly in the range [0, 1] to use in
 * interpolation)
 */
template <typename T>
concept Interpolator = std::invocable<T, f64>;
} // namespace sm::concepts
