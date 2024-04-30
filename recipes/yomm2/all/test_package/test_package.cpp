// Copyright (c) 2018-2021 Jean-Louis Leroy
// Distributed under the Boost Software License, Version 1.0.
// See accompanying file LICENSE_1_0.txt
// or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <iostream>
#include <string>

using std::string;

#include <yorel/yomm2/keywords.hpp>

using yorel::yomm2::virtual_;

struct A {
    virtual ~A() {
    }
};
struct B : A {};
struct C : A {};
struct D : B, C {};

register_class(A);
register_class(B, A);
register_class(C, A);
register_class(D, B, C);

declare_method(string, foobar, (virtual_<A&>));

define_method(string, foobar, (A&)) {
    return "foobar(A)";
}

define_method(string, foobar, (C&)) {
    return "foobar(C)";
}

#include <iostream>
#include <memory>

int main() {
    yorel::yomm2::update();

    D d;
    B& db = d; // B part of D
    C& dc = d; // C part of D
    std::cout << foobar(db) << "\n";
    std::cout << foobar(dc) << "\n";
    //std::cout << foobar(d) << "\n";
}
