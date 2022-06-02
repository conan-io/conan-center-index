/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <chrono>

#include "../core/types.hpp"

namespace sm
{
struct Stopwatch
{
    using Duration_t = std::chrono::duration<f64>;

    std::chrono::steady_clock::time_point start{std::chrono::steady_clock::now()};

    void reset();

    [[nodiscard]] auto time() const -> Duration_t;

    void print() const;
};
} // namespace sm
