/*
 * Copyright (c) 2018-2020 Morwenn.
 *
 * SPDX-License-Identifier: MIT
 */
#include <algorithm>
#include <cassert>
#include <iostream>
#include <iterator>
#include <cpp-sort/sorters/smooth_sorter.h>

int main()
{
    int arr[] = { 5, 8, 3, 2, 9 };
    cppsort::smooth_sort(arr);
    assert(std::is_sorted(std::begin(arr), std::end(arr)));

    // should print 2 3 5 8 9
    for (int val: arr) {
        std::cout << val << ' ';
    }
}
