/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "samarium/graphics/Image.hpp"
#include "samarium/graphics/colors.hpp"
#include "samarium/math/Vector2.hpp"
#include "samarium/math/interp.hpp"
#include "samarium/math/vector_math.hpp"
#include "samarium/samarium.hpp"
#include "samarium/util/random.hpp"

using namespace sm;
using namespace sm::literals;

int main()
{
    auto app = App{{.dims = dims720}};

    const auto region  = Vector2{40, 30};
    const auto samples = 10UL;
    const auto radius  = 1.0;

    auto points = sm::random.poisson_disc_points(radius, region, samples);

    auto box = app.transform.apply_inverse(app.bounding_box().template as<f64>());

    auto mapper =
        interp::make_mapper<Vector2>({{}, region}, {box.min.as<f64>(), box.max.as<f64>()});

    app.run(
        [&]
        {
            app.fill("#15151f"_c);
            for (auto point : points)
            {
                app.draw(Circle{.centre = mapper(point), .radius = radius}, "#ff1438"_c);
            }
        });
}
