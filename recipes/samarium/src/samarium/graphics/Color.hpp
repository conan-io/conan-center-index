/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <array>
#include <string_view>


#include "../core/concepts.hpp" // for u8
#include "../util/util.hpp"     // for util::strlen

namespace sm
{
struct RGB_t
{
    constexpr static auto length = 3UL;
};
struct RGBA_t
{
    constexpr static auto length = 4UL;
};
struct BGR_t
{
    constexpr static auto length = 3UL;
};
struct BGRA_t
{
    constexpr static auto length = 4UL;
};

constexpr inline auto rgb  = RGB_t{};
constexpr inline auto rgba = RGBA_t{};
constexpr inline auto bgr  = BGR_t{};
constexpr inline auto bgra = BGRA_t{};

namespace detail
{
[[nodiscard]] constexpr auto lerp(auto min, auto max, f64 factor)
{
    return min * (1. - factor) + max * factor;
}
} // namespace detail

class Color
{
  public:
    u8 r{};
    u8 g{};
    u8 b{};
    u8 a{255u};

    static constexpr auto from_double_array(const std::array<f64, 3>& colors)
    {
        return Color{static_cast<u8>(colors[0] * 255), static_cast<u8>(colors[1] * 255),
                     static_cast<u8>(colors[2] * 255)};
    }

    static constexpr auto from_double_array(const std::array<f64, 4>& colors)
    {
        return Color{static_cast<u8>(colors[0] * 255), static_cast<u8>(colors[1] * 255),
                     static_cast<u8>(colors[2] * 255), static_cast<u8>(colors[3] * 255)};
    }

    [[nodiscard]] static consteval auto from_hex(const char* str)
    {
        const auto length = util::strlen(str);

        if (str[0] != '#') { throw std::invalid_argument("Hex string must start with #"); }

        if (length != 7u && length != 9u)
        {
            throw std::invalid_argument("Hex string must be either 7 or 9 characters long");
        }

        const auto r =
            static_cast<u8>(16 * util::hex_to_int_safe(str[1]) + util::hex_to_int_safe(str[2]));
        const auto g =
            static_cast<u8>(16 * util::hex_to_int_safe(str[3]) + util::hex_to_int_safe(str[4]));
        const auto b =
            static_cast<u8>(16 * util::hex_to_int_safe(str[5]) + util::hex_to_int_safe(str[6]));

        const auto a = length == 7u ? u8{255}
                                    : static_cast<u8>(16 * util::hex_to_int_safe(str[7]) +
                                                      util::hex_to_int_safe(str[8]));
        return Color{r, g, b, a};
    }

    [[nodiscard]] static constexpr auto from_grayscale(u8 value)
    {
        return Color{value, value, value};
    }

    // https://en.m.wikipedia.org/wiki/Alpha_compositing
    constexpr auto add_alpha_over(const Color& that) noexcept
    {
        const auto alpha = 1.0 / 255 * that.a;
        r                = static_cast<u8>(that.a / 255.0 * that.r + (1.0 - alpha) * r);
        g                = static_cast<u8>(that.a / 255.0 * that.g + (1.0 - alpha) * g);
        b                = static_cast<u8>(that.a / 255.0 * that.b + (1.0 - alpha) * b);
        a                = static_cast<u8>((a / 255.0 + (1.0 - a / 255.0) * alpha) * 255);

#if 0
        // const auto alpha    = 1.0 / 255 * that.a;
        // const auto oneminus = 1.0 - alpha;
        // const auto a255     = a / 255.0;

        // r = static_cast<u8>(detail::lerp(this->r, that.r, alpha));
        // g = static_cast<u8>(detail::lerp(this->r, that.r, alpha));
        // b = static_cast<u8>(detail::lerp(this->r, that.r, alpha));
        // a = static_cast<u8>(detail::lerp(a, 1.0, alpha) * 255);

#endif // 0
    }

    [[nodiscard]] constexpr auto with_alpha(u8 alpha) const { return Color{r, g, b, alpha}; }

    [[nodiscard]] constexpr auto with_multiplied_alpha(f64 factor) const
    {
        return Color{r, g, b, static_cast<u8>(a * factor)};
    }

    template <concepts::Integral T = u8>
    [[nodiscard]] auto get_formatted(RGB_t /* color_format */) const noexcept
    {
        return std::array{static_cast<T>(this->r), static_cast<T>(this->g),
                          static_cast<T>(this->b)};
    }

    template <concepts::Integral T = u8>
    [[nodiscard]] auto get_formatted(RGBA_t /* color_format */) const noexcept
    {
        return std::array{static_cast<T>(this->r), static_cast<T>(this->g), static_cast<T>(this->b),
                          static_cast<T>(this->a)};
    }

    template <concepts::Integral T = u8>
    [[nodiscard]] auto get_formatted(BGR_t /* color_format */) const noexcept
    {
        return std::array{static_cast<T>(b), static_cast<T>(g), static_cast<T>(r)};
    }

    template <concepts::Integral T = u8>
    [[nodiscard]] auto get_formatted(BGRA_t /* color_format */) const noexcept
    {
        return std::array{static_cast<T>(b), static_cast<T>(g), static_cast<T>(r),
                          static_cast<T>(a)};
    }

    [[nodiscard]] constexpr friend auto operator==(const Color& lhs, const Color& rhs) noexcept
        -> bool = default;
};

namespace literals
{
consteval auto operator""_c(const char* str, size_t /* size */) { return Color::from_hex(str); }

} // namespace literals

namespace concepts
{
template <typename T>
concept ColorFormat = concepts::AnyOf<T, RGB_t, RGBA_t, BGR_t, BGRA_t>;
} // namespace concepts

} // namespace sm
