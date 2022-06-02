/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <filesystem>
#include <iomanip>
#include <string_view>

#ifdef __cpp_lib_source_location
#include <source_location>
#endif // __cpp_lib_source_location

#include "fmt/color.h"
#include "fmt/ranges.h"

namespace sm
{
template <typename... Args> void print(Args&&... args)
{
    // recursive call using pack expansion syntax
    (fmt::print("{} ", std::forward<Args>(args)), ...);
    fmt::print("\n");
}

template <typename T> void print_single(T&& arg) { print(std::forward<T>(arg)); }

void error(const auto&... args)
{
    fmt::print(stderr, fg(fmt::color::red) | fmt::emphasis::bold, "Error: ");
    (fmt::print(stderr, fg(fmt::color::red) | fmt::emphasis::bold, "{}", args), ...);
    fmt::print(stderr, "\n");
}

#ifdef __cpp_lib_source_location

inline void log(const std::string_view message)
{
    const std::source_location location = std::source_location::current();
    fmt::print(fg(fmt::color::steel_blue) | fmt::emphasis::bold,
               "[{}:{}: {}]:", std::filesystem::path(location.file_name()).filename().string(),
               location.line(), location.function_name());
    print(message);
}

#endif // __cpp_lib_source_location

} // namespace sm
