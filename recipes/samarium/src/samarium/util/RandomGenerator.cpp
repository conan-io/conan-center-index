/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "RandomGenerator.hpp"
#include "../math/interp.hpp"
#include "../math/vector_math.hpp"

namespace sm
{
namespace detail
{
[[nodiscard]] auto poisson_is_valid(Vector2 candidate,
                                    Vector2 sample_region,
                                    f64 cell_size,
                                    f64 radius,
                                    const std::vector<Vector2>& points,
                                    const Grid<i32>& grid)
{
    // TODO use BoundingBox
    if (!(candidate.x >= 0.0 && candidate.x < sample_region.x && candidate.y >= 0.0 &&
          candidate.y < sample_region.y))
    {
        return false;
    }

    const auto cell_x         = static_cast<i64>(candidate.x / cell_size);
    const auto cell_y         = static_cast<i64>(candidate.y / cell_size);
    const auto search_start_x = static_cast<u64>(math::max<i64>(0L, cell_x - 2L));
    const auto search_end_x =
        static_cast<u64>(math::min<i64>(cell_x + 2L, static_cast<i64>(grid.dims.x)));
    const auto search_start_y = static_cast<u64>(math::max<i64>(0L, cell_y - 2));
    const auto search_end_y =
        static_cast<u64>(math::min<i64>(cell_y + 2L, static_cast<i64>(grid.dims.y)));

    for (auto x : range(search_start_x, search_end_x))
    {
        for (auto y : range(search_start_y, search_end_y))
        {
            const auto point_index = grid[Indices{x, y}] - 1;
            if (point_index != -1 &&
                math::within_distance(candidate, points[static_cast<u64>(point_index)], radius))
            {
                return false;
            }
        }
    }
    return true;
}
} // namespace detail

void RandomGenerator::resize(u64 new_size)
{
    if (new_size < cache.size()) { return; }
    cache.resize(new_size);
    std::ranges::generate(cache, [this] { return this->next_scaled(); });
}

void RandomGenerator::reseed(u64 new_seed)
{
    inc           = new_seed;
    current_index = 0UL;
    std::ranges::generate(cache, [this] { return this->next_scaled(); });
}

[[nodiscard]] auto RandomGenerator::next() noexcept -> u64
{
    const auto oldstate = this->state;
    // Advance internal state
    this->state = oldstate * magic_number + (this->inc | 1);
    // Calculate output function (XSH RR), uses old state for max ILP
    const auto xorshifted = static_cast<u32>(((oldstate >> 18UL) ^ oldstate) >> 27UL);
    const auto rot        = static_cast<u32>(oldstate >> 59UL);
    return (xorshifted >> rot) | (xorshifted << ((-rot) & 31));
}

[[nodiscard]] auto RandomGenerator::next_scaled() noexcept -> f64
{
    return static_cast<f64>(this->next()) / static_cast<f64>(std::numeric_limits<u32>::max());
}

[[nodiscard]] auto RandomGenerator::random() -> f64
{
    if (current_index < cache.size()) { return cache[current_index++]; }

    return this->next_scaled();
}

[[nodiscard]] auto RandomGenerator::vector(const BoundingBox<f64>& bounding_box) noexcept -> Vector2
{
    return Vector2{this->range<f64>({bounding_box.min.x, bounding_box.max.x}),
                   this->range<f64>({bounding_box.min.y, bounding_box.max.y})};
}

[[nodiscard]] auto RandomGenerator::polar_vector(Extents<f64> radius_range,
                                                 Extents<f64> angle_range) noexcept -> Vector2
{
    return Vector2::from_polar({.length = this->range<f64>({radius_range.min, radius_range.max}),
                                .angle  = this->range<f64>({angle_range.min, angle_range.max})});
}

[[nodiscard]] auto RandomGenerator::poisson_disc_points(f64 radius,
                                                        Vector2 sample_region_size,
                                                        u64 sample_count) -> std::vector<Vector2>
{
    const f64 cell_size = radius / std::numbers::sqrt2;

    auto grid = Grid<i32>{{static_cast<u64>(std::ceil(sample_region_size.x / cell_size)),
                           static_cast<u64>(std::ceil(sample_region_size.y / cell_size))}};

    auto points       = std::vector<Vector2>();
    auto spawn_points = std::vector<Vector2>();

    spawn_points.push_back(sample_region_size / 2.0);

    while (!spawn_points.empty())
    {
        const auto spawn_index  = this->range<u64>({0UL, spawn_points.size() - 1UL});
        auto spawn_centre       = spawn_points[spawn_index];
        auto candidate_accepted = false;

        for (auto i : sm::range(sample_count))
        {
            std::ignore          = i;
            const auto candidate = spawn_centre + this->polar_vector({radius, 2 * radius});

            if (detail::poisson_is_valid(candidate, sample_region_size, cell_size, radius, points,
                                         grid))
            {
                points.push_back(candidate);
                spawn_points.push_back(candidate);
                grid[{static_cast<u64>(candidate.x / cell_size),
                      static_cast<u64>(candidate.y / cell_size)}] = static_cast<i32>(points.size());

                candidate_accepted = true;
                break;
            }
        }

        if (!candidate_accepted)
        {
            spawn_points.erase(spawn_points.begin() + static_cast<i64>(spawn_index));
        }
    }

    return points;
}
} // namespace sm
