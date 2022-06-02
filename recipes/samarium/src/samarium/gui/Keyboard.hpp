/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <functional>
#include <vector>

#include "SFML/Window/Keyboard.hpp"

namespace sm
{
struct Keyboard
{
    enum class Key
    {
        Unknown = -1, //!< Unhandled key
        A,            //!< The A key
        B,            //!< The B key
        C,            //!< The C key
        D,            //!< The D key
        E,            //!< The E key
        F,            //!< The F key
        G,            //!< The G key
        H,            //!< The H key
        I,            //!< The I key
        J,            //!< The J key
        K,            //!< The K key
        L,            //!< The L key
        M,            //!< The M key
        N,            //!< The N key
        O,            //!< The O key
        P,            //!< The P key
        Q,            //!< The Q key
        R,            //!< The R key
        S,            //!< The S key
        T,            //!< The T key
        U,            //!< The U key
        V,            //!< The V key
        W,            //!< The W key
        X,            //!< The X key
        Y,            //!< The Y key
        Z,            //!< The Z key
        Num0,         //!< The 0 key
        Num1,         //!< The 1 key
        Num2,         //!< The 2 key
        Num3,         //!< The 3 key
        Num4,         //!< The 4 key
        Num5,         //!< The 5 key
        Num6,         //!< The 6 key
        Num7,         //!< The 7 key
        Num8,         //!< The 8 key
        Num9,         //!< The 9 key
        Escape,       //!< The Escape key
        LControl,     //!< The left Control key
        LShift,       //!< The left Shift key
        LAlt,         //!< The left Alt key
        LSystem,   //!< The left OS specific key: window (Windows and Linux), apple (MacOS X), ...
        RControl,  //!< The right Control key
        RShift,    //!< The right Shift key
        RAlt,      //!< The right Alt key
        RSystem,   //!< The right OS specific key: window (Windows and Linux), apple (MacOS X), ...
        Menu,      //!< The Menu key
        LBracket,  //!< The [ key
        RBracket,  //!< The ] key
        Semicolon, //!< The ; key
        Comma,     //!< The , key
        Period,    //!< The . key
        Quote,     //!< The ' key
        Slash,     //!< The / key
        Backslash, //!< The \ key
        Tilde,     //!< The ~ key
        Equal,     //!< The = key
        Hyphen,    //!< The - key (hyphen)
        Space,     //!< The Space key
        Enter,     //!< The Enter/Return keys
        Backspace, //!< The Backspace key
        Tab,       //!< The Tabulation key
        PageUp,    //!< The Page up key
        PageDown,  //!< The Page down key
        End,       //!< The End key
        Home,      //!< The Home key
        Insert,    //!< The Insert key
        Delete,    //!< The Delete key
        Add,       //!< The + key
        Subtract,  //!< The - key (minus, usually from numpad)
        Multiply,  //!< The * key
        Divide,    //!< The / key
        Left,      //!< Left arrow
        Right,     //!< Right arrow
        Up,        //!< Up arrow
        Down,      //!< Down arrow
        Numpad0,   //!< The numpad 0 key
        Numpad1,   //!< The numpad 1 key
        Numpad2,   //!< The numpad 2 key
        Numpad3,   //!< The numpad 3 key
        Numpad4,   //!< The numpad 4 key
        Numpad5,   //!< The numpad 5 key
        Numpad6,   //!< The numpad 6 key
        Numpad7,   //!< The numpad 7 key
        Numpad8,   //!< The numpad 8 key
        Numpad9,   //!< The numpad 9 key
        F1,        //!< The F1 key
        F2,        //!< The F2 key
        F3,        //!< The F3 key
        F4,        //!< The F4 key
        F5,        //!< The F5 key
        F6,        //!< The F6 key
        F7,        //!< The F7 key
        F8,        //!< The F8 key
        F9,        //!< The F9 key
        F10,       //!< The F10 key
        F11,       //!< The F11 key
        F12,       //!< The F12 key
        F13,       //!< The F13 key
        F14,       //!< The F14 key
        F15,       //!< The F15 key
        Pause,     //!< The Pause key

        KeyCount //!< Keep last -- the total number of keyboard keys
    };

    static auto is_key_pressed(Key key)
    {
        return sf::Keyboard::isKeyPressed(static_cast<sf::Keyboard::Key>(key));
    }
};

class Keymap
{
    using Keys_t   = std::vector<Keyboard::Key>;
    using Action_t = std::function<void()>;

    std::vector<Keys_t> map;
    std::vector<Action_t> actions;

  public:
    Keymap() = default;

    explicit Keymap(const std::vector<std::pair<Keys_t, Action_t>>& input_keymap)
    {
        map.reserve(input_keymap.size());
        actions.reserve(input_keymap.size());

        for (const auto& [key, action] : input_keymap)
        {
            map.push_back(key);
            actions.push_back(action);
        }
    }

    void push_back(const Keys_t& keys, std::invocable auto&& fn)
    {
        map.push_back(keys);
        actions.emplace_back(fn);
    }

    void clear();

    void run() const;
};

} // namespace sm
