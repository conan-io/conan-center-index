/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "fmt/format.h"

#include "Stopwatch.hpp"

namespace sm
{
void Stopwatch::reset() { start = std::chrono::steady_clock::now(); }

auto Stopwatch::time() const -> Stopwatch::Duration_t
{
    const auto finish = std::chrono::steady_clock::now();
    return std::chrono::duration_cast<Duration_t>(finish - start);
}

void Stopwatch::print() const { fmt::print("{:.3}ms\n", this->time().count() * 1000.0); }

}; // namespace sm
