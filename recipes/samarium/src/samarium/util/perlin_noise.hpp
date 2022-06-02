/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "../math/interp.hpp"
#include "random.hpp"

namespace sm
{
struct PerlinGenerator
{
    // TODO
    // function make_perm()
    // {
    //     let P = [];
    //     for (let i = 0; i < 256; i++) { P.push(i); }
    //     Shuffle(P);
    //     for (let i = 0; i < 256; i++) { P.push(P[i]); }

    //     return P;
    // }
    // let P = MakePermutation();

    // function GetConstantVector(v)
    // {
    //     // v is the value from the permutation table
    //     let h = v & 3;
    //     if (h == 0) return new Vector2(1.0, 1.0);
    //     else if (h == 1)
    //         return new Vector2(-1.0, 1.0);
    //     else if (h == 2)
    //         return new Vector2(-1.0, -1.0);
    //     else
    //         return new Vector2(1.0, -1.0);
    // }

    // function Fade(t) { return ((6 * t - 15) * t + 10) * t * t * t; }

    // function Lerp(t, a1, a2) { return a1 + t * (a2 - a1); }

    // function Noise2D(x, y)
    // {
    //     let X = Math.floor(x) & 255;
    //     let Y = Math.floor(y) & 255;

    //     let xf = x - Math.floor(x);
    //     let yf = y - Math.floor(y);

    //     let topRight    = new Vector2(xf - 1.0, yf - 1.0);
    //     let topLeft     = new Vector2(xf, yf - 1.0);
    //     let bottomRight = new Vector2(xf - 1.0, yf);
    //     let bottomLeft  = new Vector2(xf, yf);

    //     // Select a value in the array for each of the 4 corners
    //     let valueTopRight    = P[P[X + 1] + Y + 1];
    //     let valueTopLeft     = P[P[X] + Y + 1];
    //     let valueBottomRight = P[P[X + 1] + Y];
    //     let valueBottomLeft  = P[P[X] + Y];

    //     let dotTopRight    = topRight.dot(GetConstantVector(valueTopRight));
    //     let dotTopLeft     = topLeft.dot(GetConstantVector(valueTopLeft));
    //     let dotBottomRight = bottomRight.dot(GetConstantVector(valueBottomRight));
    //     let dotBottomLeft  = bottomLeft.dot(GetConstantVector(valueBottomLeft));

    //     let u = Fade(xf);
    //     let v = Fade(yf);

    //     return Lerp(u, Lerp(v, dotBottomLeft, dotTopLeft), Lerp(v, dotBottomRight, dotTopRight));
    // }
};
} // namespace sm
