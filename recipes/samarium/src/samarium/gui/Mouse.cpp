/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "Mouse.hpp"

namespace sm
{
Vector2 Mouse::vel() const { return this->pos.now - this->pos.prev; }

void Mouse::update(const sf::RenderWindow& window)
{
    this->pos.prev = this->pos.now;
    this->pos.now  = sfml(sf::Mouse::getPosition(window)).as<f64>();
    this->left     = sf::Mouse::isButtonPressed(sf::Mouse::Left);
    this->middle   = sf::Mouse::isButtonPressed(sf::Mouse::Middle);
    this->right    = sf::Mouse::isButtonPressed(sf::Mouse::Right);
}

Transform Mouse::apply(Transform transform, Mouse::Button btn) const
{
    if ((btn == Mouse::Button::Left && this->left) || (btn == Mouse::Button::Right && this->right))
        transform.pos += this->vel();

    return transform;
}
} // namespace sm
