/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "BoundingBox.hpp"
#include "shapes.hpp"

namespace sm
{
class Transform
{
  public:
    Vector2 pos{};
    Vector2 scale{};

    [[nodiscard]] constexpr auto apply(Vector2 vec) const noexcept { return vec * scale + pos; }

    [[nodiscard]] constexpr auto apply(const BoundingBox<f64>& bounding_box) const noexcept
    {
        return BoundingBox<f64>{apply(bounding_box.min), apply(bounding_box.max)}.validated();
    }

    [[nodiscard]] constexpr auto apply_inverse(Vector2 vec) const noexcept
    {
        return (vec - pos) / scale;
    }

    [[nodiscard]] constexpr auto apply_inverse(const BoundingBox<f64>& bounding_box) const noexcept
    {
        return BoundingBox<f64>::find_min_max(
            this->apply_inverse(bounding_box.min),
            this->apply_inverse(
                bounding_box.max)); // -ve sign may invalidate min, max, so recalculate it
    }

    [[nodiscard]] constexpr auto apply_inverse(const LineSegment& l) const noexcept
    {
        return LineSegment{// -ve sign may invalidate min, max so recalculate it
                           apply_inverse(l.p1), apply_inverse(l.p2)};
    }
};
} // namespace sm
