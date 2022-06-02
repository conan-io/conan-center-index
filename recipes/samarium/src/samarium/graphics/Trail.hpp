/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <span>
#include <vector>

#include "../math/Vector2.hpp"

namespace sm
{
class Trail
{
    std::vector<Vector2> trail;

  public:
    const size_t max_length;

    explicit Trail(size_t length = 50) : max_length{length} { trail.reserve(length); }

    auto begin() noexcept { return trail.begin(); }
    auto end() noexcept { return trail.end(); }

    auto begin() const noexcept { return trail.cbegin(); }
    auto end() const noexcept { return trail.cend(); }

    auto cbegin() const noexcept { return trail.cbegin(); }
    auto cend() const noexcept { return trail.cend(); }

    auto size() const noexcept { return trail.size(); }
    auto empty() const noexcept { return trail.empty(); }

    auto operator[](u64 index) noexcept { return trail[index]; }
    auto operator[](u64 index) const noexcept { return trail[index]; }

    void push_back(Vector2 pos);

    [[nodiscard]] auto span() const -> std::span<const Vector2>;
};
} // namespace sm
