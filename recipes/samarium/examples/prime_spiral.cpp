/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

// Based on: https://youtu.be/EK32jo7i5LQ

#include "samarium/graphics/colors.hpp"
#include "samarium/samarium.hpp"

static constexpr auto scale = 80.0;

using namespace sm;
using namespace sm::literals;

auto is_prime(i32 n)
{
    for (auto i = 2; i <= n / 2; ++i)
    {
        if (n % i == 0) { return false; }
    }
    return true;
}

int main()
{
    auto app = App{{.dims = {1000, 1000}}};
    app.transform.scale /= scale; // zoom out

    const auto count = i32(app.transform.apply_inverse(Vector2{})
                               .length()); // roughly ensure numbers fill up screen by getting
                                           // distance from centre to corner

    print("Count: ", count);
    auto numbers = std::vector<i32>();

    for (auto i = 1; i32(numbers.size()) < count; i++)
    {
        if (is_prime(i)) { numbers.push_back(i); }
    }

    const auto draw = [&]
    {
        app.fill("#06060c"_c);
        if (app.mouse.left)
        {
            app.transform.pos += app.mouse.pos.now - app.mouse.pos.prev;
        } // translate

        const auto factor = 1.0 + 0.1 * app.mouse.scroll_amount;
        app.transform.scale *= Vector2::combine(factor);
        app.transform.pos = app.mouse.pos.now + factor * (app.transform.pos - app.mouse.pos.now);

        for (auto i : numbers)
        {
            app.draw(Circle{.centre = Vector2::from_polar({f64(i), f64(i)}),
                            .radius = 4.0 / std::sqrt(app.transform.scale.x)},
                     colors::aquamarine);
        }
    };
    app.run(draw);
}
