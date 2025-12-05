// Copyright 2016-2025 Antony Polukhin

// Distributed under the Boost Software License, Version 1.0.
// (See the accompanying file LICENSE_1_0.txt
// or a copy at <http://www.boost.org/LICENSE_1_0.txt>.)

#include <cassert>
#include <iostream>
#include <set>
#include <unordered_set>

#include <pfr.hpp>

void test_examples() {

#if PFR_USE_CPP17
  {
    // Assert equality.
    // Note that the equality operator for structure is not defined.

    struct test {
      std::string f1;
      std::string_view f2;
    };

    assert(pfr::eq(test{"aaa", "zomg"}, test{"aaa", "zomg"}));
  }
#endif

  {
    // Increment each field of the variable on 1 and
    // output the content of the variable.

    struct test {
      int f1;
      long f2;
    };

    test var{42, 43};

    pfr::for_each_field(var, [](auto &field) { field += 1; });

    std::cout << pfr::io(var);
  }

  {
    // Iterate over fields of a variable and output index of a variable.

    struct tag0 {};
    struct tag1 {};
    struct sample {
      tag0 a;
      tag1 b;
    };

    pfr::for_each_field(sample{}, [&](const auto &field, std::size_t idx) {
      std::cout << '\n' << idx;
    });

    std::cout << '\n';
  }

// Disabling for MSVC as it gives a hard error on using local types:
//
// error C7631:
// 'pfr::detail::do_not_use_PFR_with_local_types<test_examples::sample>':
// variable with internal linkage declared but not defined
#if PFR_CORE_NAME_ENABLED && PFR_USE_CPP17 && !defined(_MSC_VER)
  {
    // Print the name and value
    // of each element of the structure

    struct test {
      int n;
      std::string str;
    };

    test var{42, "Hello, World!"};

    pfr::for_each_field_with_name(
        var, [](std::string_view name, const auto &value) {
          std::cout << name << ": " << value << std::endl;
        });
  }
#endif

  {
    // Getting fields count of some structure

    struct some {
      int a, b, c, d, e;
    };

    std::cout << "Fields count in structure: " << pfr::tuple_size<some>::value
              << '\n';
  }

  {
    // Get field by index/type and assign new value to that field

    struct sample {
      char c;
      float f;
    };

    sample var{};
    pfr::get<1>(var) = 42.01f;
    pfr::get<char>(var) = 'A';

    std::cout << var.c << ": " << var.f << '\n';
  }

// Disabling for MSVC as it gives a hard error on using local types:
//
// error C7631:
// 'pfr::detail::do_not_use_PFR_with_local_types<test_examples::sample>':
// variable with internal linkage declared but not defined
#if PFR_CORE_NAME_ENABLED && PFR_USE_CPP17 && !defined(_MSC_VER)
  {
    // Get name of field by index

    struct sample {
      int f_int;
      long f_long;
    };

    std::cout << pfr::get_name<0, sample>() << " " << pfr::get_name<1, sample>()
              << '\n';
  }
#endif

#if PFR_USE_CPP17 || PFR_USE_LOOPHOLE
  {
    // Getting a std::tuple of values from structures fields

    struct foo {
      int a, b;
    };
    struct other {
      char c;
      foo nested;
    };

    other var{'A', {3, 4}};
    std::tuple<char, foo> t = pfr::structure_to_tuple(var);
    assert(std::get<0>(t) == 'A');
    assert(pfr::eq(std::get<1>(t), foo{3, 4}));
  }
#endif

#if PFR_USE_CPP17 || PFR_USE_LOOPHOLE
  {
    // Getting a std::tuple of references to structure fields

    struct foo {
      int a, b;
    };
    struct other {
      char c;
      foo f;
    };

    other var{'A', {14, 15}};
    std::tuple<char &, foo &> t = pfr::structure_tie(var);
    std::get<1>(t) = foo{1, 2};

    std::cout << pfr::io(var.f);
  }
#endif

} // void test_examples()

// Define all the comparison and IO operators for my_structure type along
// with hash_value function.

#include <pfr/functions_for.hpp>

namespace my_namespace {
struct my_structure {
  int a, b, c, d, e, f, g;
};
PFR_FUNCTIONS_FOR(my_structure)
} // namespace my_namespace

// Define only the equality and inequality operators for my_eq_ne_structure.

#include <pfr/functions_for.hpp>

namespace my_namespace {
struct my_eq_ne_structure {
  float a, b, c, d, e, f, g;
};

inline bool operator==(const my_eq_ne_structure &x,
                       const my_eq_ne_structure &y) {
  return pfr::eq_fields(x, y);
}

inline bool operator!=(const my_eq_ne_structure &x,
                       const my_eq_ne_structure &y) {
  return pfr::ne_fields(x, y);
}
} // namespace my_namespace

int main() { test_examples(); }