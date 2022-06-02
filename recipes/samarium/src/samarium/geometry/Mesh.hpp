/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <algorithm>
#include <ranges>
#include <vector>

#include "../math/shapes.hpp"
#include "../math/vector_math.hpp"

namespace sm
{
struct Mesh
{
    using Vertex = Vector2;

    struct Edge
    {
        u32 v1{};
        u32 v2{};
    };

    std::vector<Vertex> vertices{};
    std::vector<Edge> edges{};

    auto edges_view()
    {
        // const auto get_line_segment = [this](const auto& edge) {
        //     return LineSegment{vertices[edge.v1], vertices[edge.v2]};
        // };
        // return std::views::transform(edges, get_line_segment);
    }
};
} // namespace sm
