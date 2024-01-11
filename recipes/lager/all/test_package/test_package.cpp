// https://github.com/arximboldi/lager/blob/v0.1.1/test/deps.cpp
//
// lager - library for functional interactive c++ programs
// Copyright (C) 2017 Juan Pedro Bolivar Puente
//
// This file is part of lager.
//
// lager is free software: you can redistribute it and/or modify
// it under the terms of the MIT License, as detailed in the LICENSE
// file located at the root of this source code distribution,
// or here: <https://github.com/arximboldi/lager/blob/master/LICENSE>
//

#include <lager/deps.hpp>
#include <cassert>

struct foo
{
    int x = 0;
};

struct bar
{
    const char* s = "lol";
};

int main() {
    auto x = lager::deps<foo, bar>::with(foo{}, bar{});
    assert(x.get<foo>().x == 0);
    assert(lager::get<bar>(x).s == std::string{"lol"});
    return 0;
}
