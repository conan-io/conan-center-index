/*
 * Copyright (c) 2011 Fuji, Goro (gfx) <gfuji@cpan.org>.
 * Copyright (c) 2019 Morwenn.
 *
 * SPDX-License-Identifier: MIT
 */
#include <cstddef>
#include <iostream>
#include <gfx/timsort.hpp>

int main()
{
    const std::size_t size = 5;
    
    int arr[size] = { 5, 8, 3, 2, 9 };
    gfx::timsort(arr, arr + size);

    // should print 2 3 5 8 9
    for (std::size_t idx = 0 ; idx < size ; ++idx) {
        std::cout << arr[idx] << ' ';
    }
}
