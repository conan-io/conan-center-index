/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "fmt/format.h"

#include "ostream.hpp"

std::ostream& operator<<(std::ostream& os, const sm::Version& a)
{
    os << fmt::format("{}", a);
    return os;
}

std::ostream& operator<<(std::ostream& os, const sm::Color& a)
{
    os << fmt::format("{}", a);
    return os;
}
