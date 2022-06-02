/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "samarium/samarium.hpp"

int main()
{
    const auto im = sm::Image{};
    fmt::print(fmt::emphasis::bold, "\nSuccessful installation!\n");
    fmt::print(fmt::emphasis::bold, "Welcome to {}\n", sm::version);
    sm::print("A Vector2:", sm::Vector2{.x = 5, .y = -3});
    sm::print("A Color:  ", sm::Color{.r = 5, .g = 200, .b = 255});
}
