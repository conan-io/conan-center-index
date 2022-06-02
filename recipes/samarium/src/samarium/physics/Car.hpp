/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "../math/Vector2.hpp"


namespace sm
{
struct Car
{
    Vector2 pos{};
    f64 vel{};
    f64 acc{};

    f64 body_angle{};
    f64 turn_angle{};
    f64 left_angle{};
    f64 right_angle{};

    const f64 wheelbase{};
    const f64 track{};

    // https://www.xarg.org/book/kinematics/ackerman-steering/

    void update(f64 delta);
};
} // namespace sm
