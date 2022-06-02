# SPDX-License-Identifier: MIT Copyright (c) 2022 Jai Bellare See
# <https://opensource.org/licenses/MIT/> or LICENSE.md Project homepage:
# <https://github.com/strangeQuark1041/samarium>

# https://www.reddit.com/r/cpp/comments/t2yoay/comment/hyrgm63/

cmake_minimum_required(VERSION 3.16)

option(USE_CCACHE "Use Ccache" TRUE)
if(USE_CCACHE)
    find_program(CCACHE_PROGRAM ccache)
    if(CCACHE_PROGRAM)
        message(STATUS "ccache found: ${CCACHE_PROGRAM}")
        set(CMAKE_C_COMPILER_LAUNCHER "ccache")
        set(CMAKE_CXX_COMPILER_LAUNCHER "ccache")
    endif()
endif()
