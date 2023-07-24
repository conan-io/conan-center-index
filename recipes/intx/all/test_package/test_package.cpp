// intx: extended precision integer library.
// Copyright 2019 Pawel Bylica.
// Licensed under the Apache License, Version 2.0.

#include <intx/intx.hpp>

int main(int argc, char**)
{
    return static_cast<int>(intx::uint512{argc} / (intx::uint512{1} << 111));
}
