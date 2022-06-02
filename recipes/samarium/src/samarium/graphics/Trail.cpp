/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include <algorithm>

#include "Trail.hpp"

namespace sm
{
void Trail::push_back(Vector2 pos)
{
    if (this->max_length > this->trail.size()) { this->trail.push_back(pos); }
    else
    {
        std::rotate(this->trail.begin(), this->trail.begin() + 1, this->trail.end());
        this->trail.back() = std::move(pos);
    }
}

std::span<const Vector2> Trail::span() const
{
    return std::span(this->trail.begin(), this->trail.size());
}
} // namespace sm
