/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include "../core/types.hpp" // for u8
#include <stddef.h>          // for size_t
#include <stdexcept>         // for invalid_argument
#include <string>            // for string

namespace sm::util
{
[[nodiscard]] consteval size_t strlen(const char* str) // NOSONAR
{
    return *str ? 1u + strlen(str + 1) : 0u;
}

[[nodiscard]] consteval u8 hex_to_int_safe(char ch)
{
    if ('0' <= ch && ch <= '9') { return static_cast<u8>(ch - '0'); }
    if ('a' <= ch && ch <= 'f') { return static_cast<u8>(ch - 'a' + 10); }
    if ('A' <= ch && ch <= 'F') { return static_cast<u8>(ch - 'A' + 10); }
    throw std::invalid_argument("hex character must be 0-9, a-f, or A-F");
}
} // namespace sm::util
