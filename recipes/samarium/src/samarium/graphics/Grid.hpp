/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <compare>
#include <functional>
#include <iterator>

#include "../core/DynArray.hpp"
#include "../math/BoundingBox.hpp"
#include "../math/Extents.hpp"

#include "Color.hpp"

namespace sm
{
constexpr inline auto dims4K  = Dimensions{3840UL, 2160UL};
constexpr inline auto dimsFHD = Dimensions{1920UL, 1080UL};
constexpr inline auto dims720 = Dimensions{1280UL, 720UL};
constexpr inline auto dims480 = Dimensions{640UL, 480UL};
constexpr inline auto dimsP2  = Dimensions{2048UL, 1024UL};

constexpr auto convert_1d_to_2d(Dimensions dims, size_t index)
{
    return Indices{index % dims.x, index / dims.x};
}

constexpr auto convert_2d_to_1d(Dimensions dims, Indices coordinates)
{
    return coordinates.y * dims.x + coordinates.x;
}

template <typename T> class Grid
{
  public:
    // Container types
    using value_type      = T;
    using reference       = T&;
    using const_reference = const T&;
    using iterator        = T*;
    using const_iterator  = T const*;
    using difference_type = std::ptrdiff_t;
    using size_type       = std::size_t;

    // Public members
    std::vector<T> data;
    const Dimensions dims;

    // Constructors
    explicit Grid(Dimensions dims_ = dimsFHD) : data(dims_.x * dims_.y), dims{dims_} {}

    explicit Grid(Dimensions dims_, T init_value) : data(dims_.x * dims_.y, init_value), dims{dims_}
    {
    }

    template <typename Fn>
    requires std::invocable<Fn, Indices>
    static auto generate(Dimensions dims, Fn&& fn)
    {
        auto grid = Grid<T>(dims);
        for (auto y : range(dims.y))
        {
            for (auto x : range(dims.x))
            {
                const auto pos = Indices{x, y};
                grid[pos]      = fn(pos);
            }
        }
        return grid;
    }

    // -------------------------------Member functions------------------------------------

    auto operator[](Indices indices) -> T&
    {
        return this->data[indices.y * this->dims.x + indices.x];
    }
    auto operator[](Indices indices) const -> const T&
    {
        return this->data[indices.y * this->dims.x + indices.x];
    }

    auto operator[](size_t index) noexcept -> T& { return this->data[index]; }
    auto operator[](size_t index) const noexcept -> const T& { return this->data[index]; }

    auto at(Indices indices) -> T&
    {
        if (indices.x >= dims.x || indices.y >= dims.y)
        {
            throw std::out_of_range(
                fmt::format("sm::Grid: indices [{}, {}] out of range for dimensions [{}, {}]",
                            indices.x, indices.y, this->dims.x, this->dims.y));
        }

        return this->operator[](indices);
    }

    auto at(Indices indices) const -> const T&
    {
        if (indices.x >= dims.x || indices.y >= dims.y)
        {
            throw std::out_of_range(
                fmt::format("sm::Grid: indices [{}, {}] out of range for dimensions [{}, {}]",
                            indices.x, indices.y, this->dims.x, this->dims.y));
        }

        return this->operator[](indices);
    }

    auto at(size_t index) -> T&
    {
        if (index >= this->m_size)
        {
            throw std::out_of_range(
                fmt::format("sm::Grid: index {} out of range for size {}", index, this->m_size));
        }

        return this->data[index];
    }

    auto at(size_t index) const -> const T&
    {
        if (index >= this->m_size)
        {
            throw std::out_of_range(
                fmt::format("sm::Grid: index {} out of range for size {}", index, this->m_size));
        }

        return this->data[index];
    }

    auto begin() { return this->data.begin(); }
    auto end() { return this->data.end(); }

    auto begin() const { return this->data.cbegin(); }
    auto end() const { return this->data.cend(); }

    auto cbegin() const { return this->data.cbegin(); }
    auto cend() const { return this->data.cend(); }

    auto size() const { return this->data.size(); }
    auto max_size() const { return this->data.size(); } // for stl compatibility
    auto empty() const { return this->data.size() == 0; }

    auto bounding_box() const { return BoundingBox<size_t>{Indices{}, dims - Indices{1, 1}}; }

    auto fill(const T& value) { this->data.fill(value); }

    template <concepts::ColorFormat Format>
    [[nodiscard]] auto formatted_data(Format format) const
        -> DynArray<std::array<u8, Format::length>>
    {
        const auto format_length = Format::length;
        auto fmt_data            = DynArray<std::array<u8, format_length>>(this->size());

        std::transform(this->begin(), this->end(), fmt_data.begin(),
                       [format](auto color) { return color.get_formatted(format); });

        return fmt_data;
    }

    [[nodiscard]] auto upscale(u64 upscale_factor) const
    {
        auto output = Grid<T>(this->dims * upscale_factor);
        for (auto y : range(output.dims.y))
        {
            for (auto x : range(output.dims.x))
            {
                output[{x, y}] = this->operator[](Indices{x, y} / upscale_factor);
            }
        }

        return output;
    }

    struct Iterator2d
    {
        using iterator_category = std::forward_iterator_tag;
        using difference_type   = std::ptrdiff_t;
        using value_type        = std::pair<Indices, T*>;
        using pointer           = value_type*; // or also value_type*
        using reference         = value_type;  // or also value_type&

        Grid<T>& grid;
        u64 index;

        auto operator*() const -> reference
        {
            return value_type{convert_1d_to_2d(grid.dims, index), &grid[index]};
        }
        // auto operator->() -> pointer { return &(grid->operator[](m_index)); }

        // Prefix increment
        auto operator++() -> Iterator2d&
        {
            index++;
            return *this;
        }

        // Postfix increment
        auto operator++(int) -> Iterator2d
        {
            Iterator2d tmp = *this;
            ++(*this);
            return tmp;
        }

        friend auto operator==(const Iterator2d& a, const Iterator2d& b) -> bool
        {
            return a.index == b.index;
        };
    };

    struct Iterator2dHolder
    {
        Grid<T>& grid;
        auto begin() { return Iterator2d{this->grid, 0}; }
        auto end() { return Iterator2d{this->grid, this->grid.size()}; }
        auto size() const { return this->grid.size(); }
    };

    auto iterate_2d() { return Iterator2dHolder{*this}; }
};

} // namespace sm
