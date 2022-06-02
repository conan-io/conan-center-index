/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <algorithm>
#include <iterator>
#include <span>
#include <stdexcept>

#include "fmt/format.h"

namespace sm
{
template <typename T> struct DynArray
{
    // Container types
    using value_type      = T;
    using reference       = T&;
    using const_reference = const T&;
    using iterator        = T*;
    using const_iterator  = T const*;
    using difference_type = std::ptrdiff_t;
    using size_type       = std::size_t;

    // Constructors
    explicit DynArray(size_t size_ = {}) : data(new T[size_]{}), m_size(size_) {} // NOSONAR

    explicit DynArray(size_t size_, T init_value) : data(new T[size_]), m_size(size_)
    {
        std::fill(&this->data[0], &this->data[size_], init_value);
    }

    DynArray(const DynArray& arr) : data(new T[arr.m_size]), m_size(arr.m_size)
    {
        std::copy(arr.begin(), arr.end(), this->data);
    }

    DynArray(DynArray&& arr) noexcept : m_size(arr.m_size) { std::swap(data, arr.data); }

    // Operator overloads
    auto operator=(const DynArray& arr) -> DynArray&
    {
        std::copy(arr.begin(), arr.end(), this->data);
        return *this;
    }

    auto operator=(DynArray&& other) noexcept -> DynArray&
    {
        data   = std::move(other.data);
        m_size = std::move(other.m_size);
        return *this;
    }

    auto operator[](size_t index) noexcept -> T& { return this->data[index]; }

    auto operator[](size_t index) const noexcept -> const T& { return this->data[index]; }

    auto at(size_t index) -> T&
    {
        if (index >= this->m_size)
        {
            throw std::out_of_range(fmt::format("sm::DynArray: index {} out of range for size {}",
                                                index, this->m_size));
        }

        return this->data[index];
    }

    auto at(size_t index) const -> const T&
    {
        if (index >= this->m_size)
        {
            throw std::out_of_range(fmt::format("sm::DynArray: index {} out of range for size {}",
                                                index, this->m_size));
        }

        return this->data[index];
    }

    auto begin() noexcept { return static_cast<iterator>(&this->data[0]); }
    auto end() noexcept { return static_cast<iterator>(&this->data[this->m_size]); }

    auto begin() const noexcept { return static_cast<const_iterator>(&this->data[0]); }
    auto end() const noexcept { return static_cast<const_iterator>(&this->data[this->m_size]); }

    auto cbegin() const noexcept { return static_cast<const_iterator>(&this->data[0]); }
    auto cend() const noexcept { return static_cast<const_iterator>(&this->data[this->m_size]); }

    auto size() const noexcept { return this->m_size; }
    auto empty() const noexcept { return this->m_size == 0; }

    auto as_span() noexcept { return std::span{this->begin(), this->m_size}; }

    auto fill(const T& value) { std::fill(this->begin(), this->end(), value); }

    ~DynArray() { delete[] data; }

  private:
    T* data;
    const size_t m_size;
};
} // namespace sm
