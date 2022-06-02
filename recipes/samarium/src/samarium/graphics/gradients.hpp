/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "Gradient.hpp"

namespace sm::gradients
{
constexpr inline auto blue       = Gradient{Color{101, 199, 247}, Color{0, 82, 212}};
constexpr inline auto purple     = Gradient{Color{142, 45, 226}, Color{74, 0, 224}};
constexpr inline auto blue_green = Gradient{Color{0, 242, 96}, Color{5, 117, 230}};
constexpr inline auto horizon    = Gradient{Color{18, 194, 233}, Color{246, 79, 89}};
constexpr inline auto heat = Gradient{Color{27, 9, 128}, Color{107, 21, 21}, Color{255, 126, 40},
                                      Color{255, 0, 255}, Color{0, 255, 255}};
constexpr inline auto rainbow =
    Gradient{Color{148, 0, 211}, Color{75, 0, 130},  Color{0, 0, 255}, Color{0, 255, 0},
             Color{255, 255, 0}, Color{255, 127, 0}, Color{255, 0, 0}};
constexpr inline auto magma =
    Gradient{Color::from_double_array(std::array{0.001462, 0.000466, 0.013866}),
             Color::from_double_array(std::array{0.439062, 0.120298, 0.506555}),
             Color::from_double_array(std::array{0.944006, 0.377643, 0.365136}),
             Color::from_double_array(std::array{0.987053, 0.991438, 0.749504})};
} // namespace sm::gradients
