/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "../../graphics/Image.hpp"
#include "../../math/Extents.hpp"

namespace sm
{
struct Fluid
{
    u64 size{512};

    f64 dt{0.2};
    f64 diff{0.1};
    f64 visc{0.0000001};

    ScalarField s{{size * size}};
    ScalarField density{{size * size}};

    ScalarField Vx{{size * size}};
    ScalarField Vy{{size * size}};

    ScalarField Vx0{{size * size}};
    ScalarField Vy0{{size * size}};

    void add_density(Indices pos, f64 amount) { this->density[pos] += amount; }

    void add_velocity(Indices pos, f64 amountX, f64 amountY)
    {
        this->Vx[pos] += amountX;
        this->Vy[pos] += amountY;
    }

    void update()
    {
        diffuse(1, Vx0, Vx, visc, dt);
        diffuse(2, Vy0, Vy, visc, dt);

        project(Vx0, Vy0, Vx, Vy);

        advect(1, Vx, Vx0, Vx0, Vy0, dt);
        advect(2, Vy, Vy0, Vx0, Vy0, dt);

        project(Vx, Vy, Vx0, Vy0);

        diffuse(0, s, density, diff, dt);
        advect(0, density, s, Vx, Vy, dt);
    }

    void set_bnd(int b, ScalarField& x)
    {
        for (auto i : range(1, size - 1))
        {
            x[{i, 0}]        = b == 2 ? -x[{i, 1}] : x[{i, 1}];
            x[{i, size - 1}] = b == 2 ? -x[{i, size - 2}] : x[{i, size - 2}];
        }

        for (auto j : range(1, size - 1))
        {
            x[{0, j}]        = b == 1 ? -x[{1, j}] : x[{1, j}];
            x[{size - 1, j}] = b == 1 ? -x[{size - 2, j}] : x[{size - 2, j}];
        }

        x[{0, 0}]               = 0.5 * (x[{1, 0}] + x[{0, 1}]);
        x[{0, size - 1}]        = 0.5 * (x[{1, size - 1}] + x[{0, size - 2}]);
        x[{size - 1, 0}]        = 0.5 * (x[{size - 2, 0}] + x[{size - 1, 1}]);
        x[{size - 1, size - 1}] = 0.5 * (x[{size - 2, size - 1}] + x[{size - 1, size - 2}]);
    }

    void diffuse(int b, ScalarField& x, const ScalarField& x0, f64 diff_, f64 dt_)
    {
        f64 a = dt_ * diff_ * static_cast<f64>((size - 2) * (size - 2));
        lin_solve(b, x, x0, a, 1 + 4 * a);
    }

    void lin_solve(int b, ScalarField& x, const ScalarField& x0, f64 a, f64 c, u64 iter = 4)
    {
        f64 cRecip = 1.0 / c;
        for (auto k : range(iter))
        {
            std::ignore = k;

            for (auto j : range(1, size - 1))
            {
                for (auto i : range(1, size - 1))
                {
                    x[{i, j}] = (x0[{i, j}] + a * (x[{i + 1, j}] + x[{i - 1, j}] + x[{i, j + 1}] +
                                                   x[{i, j - 1}])) *
                                cRecip;
                }
            }

            set_bnd(b, x);
        }
    }

    void project(ScalarField& velocX, ScalarField& velocY, ScalarField& p, ScalarField& div)
    {
        for (auto j : range(1, size - 1))
        {
            for (auto i : range(1, size - 1))
            {
                div[{i, j}] = -0.5 *
                              (velocX[{i + 1, j}] - velocX[{i - 1, j}] + velocY[{i, j + 1}] -
                               velocY[{i, j - 1}]) /
                              static_cast<f64>(size);
                p[{i, j}] = 0;
            }
        }

        set_bnd(0, div);
        set_bnd(0, p);
        lin_solve(0, p, div, 1, 4);

        for (auto j : range(1, size - 1))
        {
            for (auto i : range(1, size - 1))
            {
                velocX[{i, j}] -= 0.5 * (p[{i + 1, j}] - p[{i - 1, j}]) * static_cast<f64>(size);
                velocY[{i, j}] -= 0.5 * (p[{i, j + 1}] - p[{i, j - 1}]) * static_cast<f64>(size);
            }
        }
        set_bnd(1, velocX);
        set_bnd(2, velocY);
    }

    void advect(
        int b, ScalarField& d, ScalarField& d0, ScalarField& velocX, ScalarField& velocY, f64 dt_)
    {
        f64 dtx    = dt_ * static_cast<f64>(size - 2);
        f64 dty    = dt_ * static_cast<f64>(size - 2);
        f64 Nfloat = static_cast<f64>(size);

        for (auto j : range(1, size - 1))
        {
            const auto jfloat = static_cast<f64>(j);

            for (auto i : range(1, size - 1))
            {
                const auto ifloat = static_cast<f64>(i);

                const f64 tmp1 = dtx * velocX[{i, j}];
                const f64 tmp2 = dty * velocY[{i, j}];

                f64 x = ifloat - tmp1;
                f64 y = jfloat - tmp2;

                if (x < 0.5) x = 0.5;
                if (x > Nfloat + 0.5) x = Nfloat + 0.5;
                f64 i0 = std::floor(x);
                f64 i1 = i0 + 1.0;
                if (y < 0.5) y = 0.5;
                if (y > Nfloat + 0.5) y = Nfloat + 0.5;
                f64 j0 = std::floor(y);
                f64 j1 = j0 + 1.0;

                f64 s1 = x - i0;
                f64 s0 = 1.0 - s1;
                f64 t1 = y - j0;
                f64 t0 = 1.0 - t1;

                u64 i0i = static_cast<u64>(i0);
                u64 i1i = static_cast<u64>(i1);
                u64 j0i = static_cast<u64>(j0);
                u64 j1i = static_cast<u64>(j1);

                // DOUBLE CHECK THIS!!!
                d[{i, j}] = s0 * (t0 * d0[{i0i, j0i}] + t1 * d0[{i0i, j1i}]) +
                            s1 * (t0 * d0[{i1i, j0i}] + t1 * d0[{i1i, j1i}]);
            }
        }

        set_bnd(b, d);
    }

    Image to_image() const
    {
        auto image = Image{{size, size}};
        for (auto y : range(size))
            for (auto x : range(size))
            {
                const auto pos   = Indices{x, y};
                const auto value = density[pos];
                // image[pos]       = Color::from_double_array(std::array{value, value, value});
            };

        return image;
    }
};
} // namespace sm
