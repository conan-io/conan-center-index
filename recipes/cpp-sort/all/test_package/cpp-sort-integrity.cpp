/*
 * Copyright (c) 2018-2019 Morwenn.
 *
 * SPDX-License-Identifier: MIT
 */
#include <algorithm>
#include <cassert>
#include <iostream>
#include <iterator>
#include <cpp-sort/sort.h>

int main()
{
    int arr[] = { 5, 8, 3, 2, 9 };
    cppsort::sort(arr);
    assert(std::is_sorted(std::begin(arr), std::end(arr)));

    // should print 2 3 5 8 9
    for (int val: arr) {
        std::cout << val << ' ';
    }
}
