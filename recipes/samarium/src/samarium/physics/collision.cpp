/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "collision.hpp"
#include "samarium/math/Vector2.hpp"
#include "samarium/util/print.hpp"

namespace sm::phys
{
[[nodiscard]] auto did_collide(const Particle& p1, const Particle& p2) -> std::optional<Vector2>
{
    if (math::distance(p1.pos, p2.pos) <= p1.radius + p2.radius)
    {
        return std::optional((p1.pos + p2.pos) / 2.0);
    }
    else
    {
        return std::nullopt;
    }
}

void collide(Particle& p1, Particle& p2)
{
    /*
        https://courses.lumenlearning.com/boundless-physics/chapter/collisions/#:~:text=particles%20are%20involved%20in%20an-,elastic%20collision,-%2C%20the%20velocity%20of%20the%20first

        https://www.khanacademy.org/science/physics/linear-momentum/elastic-and-inelastic-collisions/a/what-are-elastic-and-inelastic-collisions
    */

    if (&p1 == &p2) { return; } // prevent self-intersection

    if (const auto point = did_collide(p1, p2))
    {
        const auto shift  = (p1.radius + (math::distance(p1.pos, p2.pos) - p2.radius)) / 2;
        const auto centre = p1.pos + (p2.pos - p1.pos).with_length(shift);
        p1.pos            = centre + (p1.pos - centre).with_length(p1.radius);
        p2.pos            = centre + (p2.pos - centre).with_length(p2.radius);

        const auto sum    = p1.mass + p2.mass;
        const auto diff   = p1.mass - p2.mass;
        const auto coeff1 = diff / sum;
        const auto coeff2 = 2 / sum;

        const auto vel1 = Vector2{(coeff1 * p1.vel.x) + (coeff2 * p2.mass * p2.vel.x),
                                  (coeff1 * p1.vel.y) + (coeff2 * p2.mass * p2.vel.y)};
        const auto vel2 = Vector2{(coeff2 * p1.mass * p1.vel.x) + (-coeff1 * p2.vel.x),
                                  (coeff2 * p1.mass * p1.vel.y) + (-coeff1 * p2.vel.y)};

        p1.vel = vel1;
        p2.vel = vel2;
    }
}

[[nodiscard]] auto did_collide(const Particle& now, const Particle& prev, const LineSegment& l)
    -> std::optional<Vector2>
{
    const auto proj = math::project(prev.pos, l);
    const auto radius_shift =
        (proj - prev.pos)
            .with_length(prev.radius); // keep track of the point on the circumference of
                                       // prev closest to l, which will cross l first

    return math::clamped_intersection({prev.pos + radius_shift, now.pos + radius_shift}, l);
}

void collide(Dual<Particle>& p, const LineSegment& l)
{
    const auto vec = l.vector();

    const auto proj = math::project(p.prev.pos, l);

    const auto normal_vector = p.now.pos - proj;

    const auto radius_shift =
        (proj - p.prev.pos)
            .with_length(p.prev.radius); // keep track of the point on the circumference of
                                         // prev closest to l, which will cross l first

    const auto possible_collision =
        math::clamped_intersection({p.prev.pos + radius_shift, p.now.pos + radius_shift}, l);

    if (!possible_collision) { return; }

    const auto point = *possible_collision;

    auto leftover_vel = p.now.pos + radius_shift - point;
    leftover_vel.reflect(vec);
    p.now.vel.reflect(vec);
    p.now.pos = point + leftover_vel - radius_shift + normal_vector.with_length(0.05);
}
} // namespace sm::phys
