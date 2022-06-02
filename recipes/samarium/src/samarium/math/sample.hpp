/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <vector>

#include "../util/FunctionRef.hpp"

#include "Extents.hpp"

namespace sm::math
{
/**
 * @brief               Sample a function at n values
 *
 * @tparam Input        Type of input to function
 * @tparam Output       Return type of function
 * @param  function     Input function to sample
 * @param  from         Start of range (inclusive)
 * @param  to           End of range (exclusive)
 * @param  steps        Number of times to sample
 * @return std::vector<Output>
 */
template <typename Input, typename Output>
auto sample(FunctionRef<Output(Input)> function, Input from, Input to, u64 steps)
{
    auto vec             = std::vector<Output>(steps);
    const auto step_size = (to - from) / static_cast<Input>(steps);

    for (auto i : range(steps)) { vec[i] = function(static_cast<Input>(i) * step_size); }

    return vec;
}

/**
 * @brief               Integrate a function by sampling at n values and summing
 *
 * @tparam Input        Type of input to function
 * @tparam Output       Return type of function
 * @param  function     Input function to sample
 * @param  from         Start of range (inclusive)
 * @param  to           End of range (exclusive)
 * @param  steps        Number of times to sample
 * @return std::vector<Output>
 */
template <typename Output = f64, typename Input = f64>
auto integral(FunctionRef<Output(Input)> function, Input from, Input to, u64 steps)
{
    auto sum             = Output{};
    const auto step_size = (to - from) / static_cast<Input>(steps);

    for (auto i = from; i < to; i += step_size)
    {
        sum += function(static_cast<Input>(i)) * step_size;
    }

    return sum;
}
} // namespace sm::math
