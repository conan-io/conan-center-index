/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <concepts>
#include <iterator>

#include "types.hpp"

namespace sm::concepts
{

constexpr auto reason(const char* const /* reason_string */) { return true; };

template <typename T>
concept Integral =
    reason("NOTE: T should be of integral type, eg int or size_t") && std::is_integral_v<T>;

template <typename T>
concept FloatingPoint = reason(
    "NOTE: T should be of floating point type, eg float or double") && std::is_floating_point_v<T>;

template <typename T>
concept Number = Integral<T> || FloatingPoint<T>;

template <typename T>
concept Arithmetic = requires(T a, T b)
{
    {
        a + b
        } -> std::same_as<T>;
    {
        a - b
        } -> std::same_as<T>;
};

template <typename T, typename... U>
concept AnyOf = (std::same_as<T, U> || ...);

template <class T>
concept Range = requires(T&& t)
{
    std::begin(t);
    std::end(t);
    std::cbegin(t);
    std::cend(t);
    std::size(t);
};
} // namespace sm::concepts
