/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "samarium/graphics/colors.hpp"
#include "samarium/samarium.hpp"

using namespace sm;
using namespace sm::literals;

struct particle_t
{
    Vector2 pos{};
    Vector2 vel;
    f64 speed;
    Vector2 old_pos{pos};
};

struct Fluid
{

};


int main()
{
    auto app = App{{.dims = {1000, 1000}}};
    auto fluid = Fluid{};

    const auto draw = [&] { app.fill("#06060c"_c); };
    app.run(draw);
}
