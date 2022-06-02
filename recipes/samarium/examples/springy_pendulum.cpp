/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "samarium/graphics/colors.hpp"
#include "samarium/graphics/gradients.hpp"
#include "samarium/samarium.hpp"

using namespace sm;
using namespace sm::literals;

int main()
{
    auto app = App{{.dims = dims720}};

    const auto gravity = -100.0_y;

    const Vector2 anchor       = 30.0_y;
    const auto rest_length     = 14.0;
    const auto spring_constant = 100.0;

    auto p1 = Particle{.pos = {}, .vel = {50, 0}, .radius = 3, .mass = 40, .color = colors::red};
    auto p2 = p1;

    const auto l = LineSegment{{-30, -30}, {30, -9}};

    const auto viewport_box = app.viewport_box();

    const auto update = [&]
    {
        app.fill(Color{16, 18, 20});
        p1.apply_force(p1.mass * gravity);
        const auto spring = p1.pos - anchor;
        const auto force  = spring.with_length(spring_constant * (rest_length - spring.length()));
        p1.apply_force(force);
        p1.update();
        auto dual = Dual<Particle>{p1, p2};
        phys::collide(dual, l);

        for (auto&& i : viewport_box) { phys::collide(dual, i); }

        std::tie(p1, p2) = std::tuple{dual.now, dual.prev};

        app.draw_line_segment(l, "#427bf5"_c, 0.4);
        app.draw_line_segment(LineSegment{anchor, p1.pos}, "#c471ed"_c, .6);
        app.draw(p1);
        p2 = p1;
    };

    app.run(update);
}
