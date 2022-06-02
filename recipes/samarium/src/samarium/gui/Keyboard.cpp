/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "Keyboard.hpp"

namespace sm
{
void Keymap::clear()
{
    this->map.clear();
    this->actions.clear();
}

void Keymap::run() const
{
    for (size_t i = 0; i < map.size(); i++)
    {
        for (auto key : map[i])
        {
            if (!Keyboard::is_key_pressed(key)) return;
        }

        actions[i]();
    }
}
} // namespace sm
