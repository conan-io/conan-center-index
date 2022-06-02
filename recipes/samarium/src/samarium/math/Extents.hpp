/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <compare>
#include <iterator>

#include "../core/concepts.hpp"

namespace sm
{
template <typename T> struct Extents
{
    T min{};
    T max{};

    [[nodiscard]] static constexpr auto find_min_max(T a, T b) noexcept
    {
        return (a < b) ? Extents{a, b} : Extents{b, a};
    }

    [[nodiscard]] constexpr auto size() const noexcept { return max - min; }

    [[nodiscard]] constexpr auto contains(T value) const noexcept
    {
        return min <= value && value <= max;
    }

    [[nodiscard]] constexpr auto clamp(T value) const noexcept
    {
        if (value < min) { return min; }
        else if (value > max)
        {
            return max;
        }
        else
        {
            return value;
        }
    }

    [[nodiscard]] constexpr auto lerp(f64 factor) const noexcept requires concepts::Number<T>
    {
        return static_cast<f64>(min) * (1.0 - factor) +
               static_cast<f64>(max) * factor; // prevent conversion warnings
    }

    [[nodiscard]] constexpr auto lerp(f64 factor) const noexcept requires(!concepts::Number<T>)
    {
        return min * (1.0 - factor) + max * factor;
    }

    [[nodiscard]] constexpr auto clamped_lerp(f64 factor) const noexcept
    {
        return min * (1.0 - this->clamp(factor)) + max * factor;
    }

    [[nodiscard]] constexpr auto lerp_inverse(T value) const noexcept -> f64
    {
        return (value - min) / this->size();
    }

    template <typename Function>
    constexpr auto
    for_each(Function&& fn) const requires concepts::Integral<T> && std::invocable<Function, T>
    {
        for (auto i = min; i <= max; i++) { fn(i); }
    }

    struct Iterator
    {
        using iterator_category = std::contiguous_iterator_tag;
        using difference_type   = T;
        using value_type        = T;
        using pointer           = T*; // or also value_type*
        using reference         = T;  // or also value_type&

        T index;

        constexpr auto operator<=>(const Iterator&) const noexcept = default;

        constexpr auto operator*() const noexcept -> reference { return index; }

        constexpr auto operator->() noexcept -> pointer { return &index; }

        // Prefix increment
        constexpr auto operator++() noexcept -> Iterator&
        {
            index++;
            return *this;
        }

        // Postfix increment
        constexpr auto operator++(int) noexcept -> Iterator
        {
            Iterator tmp = *this;
            ++(*this);
            return tmp;
        }
    };

    [[nodiscard]] constexpr auto begin() const noexcept requires concepts::Integral<T>
    {
        return Iterator{min};
    }

    [[nodiscard]] constexpr auto end() const noexcept requires concepts::Integral<T>
    {
        return Iterator{max};
    }

    [[nodiscard]] constexpr auto operator[](u64 index) const { return min + index; }

    template <typename U> [[nodiscard]] constexpr auto as() const noexcept
    {
        return Extents<U>{static_cast<U>(min), static_cast<U>(max)};
    }
};


[[nodiscard]] constexpr auto range(u64 max) { return Extents<u64>{0UL, max}; }

[[nodiscard]] constexpr auto range(u64 min, u64 max) { return Extents<u64>{min, max}; }

[[nodiscard]] constexpr auto irange(i32 max) { return Extents<i32>{0, max}; }

[[nodiscard]] constexpr auto irange(i32 min, i32 max) { return Extents<i32>{min, max}; }
} // namespace sm
