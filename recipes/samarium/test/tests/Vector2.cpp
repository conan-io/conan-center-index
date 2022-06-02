/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include <cmath>            // for sqrt
#include <exception>        // for exception
#include <initializer_list> // for initializer_list
#include <optional>         // for optional
#include <type_traits>      // for is_same_v
#include <vector>           // for vector

#include "../ut.hpp" // for testing

#include "../../src/samarium/core/types.hpp"       // for f64
#include "../../src/samarium/math/BoundingBox.hpp" // for BoundingBox
#include "../../src/samarium/math/Vector2.hpp"     // for Vector2_t, operator==
#include "../../src/samarium/math/math.hpp"        // for almost_equal, to_rad...
#include "../../src/samarium/math/shapes.hpp"      // for Circle
#include "../../src/samarium/math/vector_math.hpp" // for clamped_intersection

using namespace boost::ut;

boost::ut::suite _Vector2 = []
{
    "math.Vector2.literals"_test = []
    {
        using namespace sm::literals;

        const auto a_x = 1.0_x;
        const auto b_x = sm::Vector2{1.0, 0};
        expect(a_x == b_x);

        const auto a_y = 1.0_y;
        const auto b_y = sm::Vector2{0, 1.0};
        expect(a_y == b_y);
    };

    "math.Vector2"_test = []
    {
        static_assert(std::is_same_v<sm::Vector2::value_type, sm::f64>);

        should("x vector") = []
        {
            const auto a = sm::Vector2{1.0, 0.0};
            expect(sm::math::almost_equal(a.length(), 1.0));
            expect(sm::math::almost_equal(a.length_sq(), 1.0));
            expect(sm::math::almost_equal(a.angle(), 0.0));
            expect(sm::math::almost_equal(a.slope(), 0.0));
        };

        should("xy vector") = []
        {
            const auto b = sm::Vector2{1.0, 1.0};
            expect(sm::math::almost_equal(b.length(), std::sqrt(2.0)));
            expect(sm::math::almost_equal(b.length_sq(), 2.0));
            expect(sm::math::almost_equal(b.angle(), sm::math::to_radians(45.0)));
            expect(sm::math::almost_equal(b.slope(), 1.0));
        };

        should("y vector") = []
        {
            const auto c = sm::Vector2{0.0, 1.0};
            expect(sm::math::almost_equal(c.length(), 1.0));
            expect(sm::math::almost_equal(c.length_sq(), 1.0));
            expect(sm::math::almost_equal(c.angle(), sm::math::to_radians(90.0)));
        };

        should("origin vector") = []
        {
            const auto d = sm::Vector2{0.0, 0.0};
            expect(sm::math::almost_equal(d.length(), 0.0));
            expect(sm::math::almost_equal(d.length_sq(), 0.0));
        };
    };

    "math.Vector2.geometry"_test = []
    {
        should("intersection") = []
        {
            should("free") = []
            {
                const auto a =
                    sm::math::intersection({{-1.0, 0.0}, {1.0, 0.0}}, {{0.0, 1.0}, {0.0, -1.0}});
                expect(a.has_value());
                expect(*a == sm::Vector2{});

                const auto b =
                    sm::math::intersection({{-1.0, -1.0}, {1.0, 1.0}}, {{1.0, -1.0}, {-1.0, 1.0}});
                expect(b.has_value());
                expect(*b == sm::Vector2{});

                const auto c = sm::math::intersection({{}, {0.0, 1.0}}, {{1.0, 0.0}, {1.0, 1.0}});
                expect(!c.has_value());
            };

            should("clamped") = []
            {
                const auto a = sm::math::clamped_intersection({{-1.0, 0.0}, {1.0, 0.0}},
                                                              {{0.0, 1.0}, {0.0, -1.0}});
                expect(a.has_value());
                expect(*a == sm::Vector2{});

                const auto b = sm::math::clamped_intersection({{-1.0, -1.0}, {1.0, 1.0}},
                                                              {{1.0, -1.0}, {-1.0, 1.0}});
                expect(b.has_value());
                expect(*b == sm::Vector2{});

                const auto c = sm::math::clamped_intersection({{-1.0, -1.0}, {-0.5, -0.5}},
                                                              {{1.0, -1.0}, {0.5, -0.5}});
                expect(!c.has_value());

                const auto d = sm::math::clamped_intersection({{-1.0, 0.0}, {-0.5, 0.0}},
                                                              {{0.0, 1.0}, {0.0, 0.5}});
                expect(!d.has_value());

                const auto e =
                    sm::math::clamped_intersection({{}, {0.0, 1.0}}, {{1.0, 0.0}, {1.0, 1.0}});
                expect(!e.has_value());
            };
        };

        should("area") = []
        {
            should("Circle") = []
            {
                expect(sm::math::area(sm::Circle{}) == 0.0_d);
                expect(sm::math::almost_equal(sm::math::area(sm::Circle{.radius = 12.0}),
                                              452.3893421169302));
            };

            should("BoundingBox") = []
            {
                expect(sm::math::area(sm::BoundingBox<double>{}) == 0.0_d);
                expect(sm::math::area(sm::BoundingBox<double>{{-10.0, -11.0}, {12.0, 13.0}}) ==
                       528.0_d);
            };
        };
    };
};
