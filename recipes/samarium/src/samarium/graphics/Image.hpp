/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "Grid.hpp"

namespace sm
{
using Image       = Grid<Color>;
using ScalarField = Grid<f64>;
using VectorField = Grid<Vector2>;
} // namespace sm
