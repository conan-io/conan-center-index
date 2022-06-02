/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

// https://stackoverflow.com/a/62485211/17100530

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#define VC_EXTRALEAN
#include <Windows.h>
#elif defined(__linux__)
#include <stdio.h>
#include <sys/ioctl.h>
#include <unistd.h>
#endif // Windows/Linux

#include "../math/Vector2.hpp"

namespace sm::util
{
Dimensions get_terminal_dims()
{
#if defined(_WIN32)
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    GetConsoleScreenBufferInfo(GetStdHandle(STD_OUTPUT_HANDLE), &csbi);
    return Dimensions{static_cast<u32>(csbi.srWindow.Right - csbi.srWindow.Left) + 1u,
                      static_cast<u32>(csbi.srWindow.Bottom - csbi.srWindow.Top) + 1u};
#elif defined(__linux__)
    struct winsize w;
    ioctl(fileno(stdout), TIOCGWINSZ, &w);
    return {static_cast<u32>(w.ws_col), static_cast<u32>(w.ws_row)};
#endif // Windows/Linux
}
} // namespace sm::util
