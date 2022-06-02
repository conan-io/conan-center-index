# SPDX-License-Identifier: MIT Copyright (c) 2022 Jai Bellare See
# <https://opensource.org/licenses/MIT/> or LICENSE.md Project homepage:
# <https://github.com/strangeQuark1041/samarium>

cmake_minimum_required(VERSION 3.16)

function(generate_coverage target)
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND GENERATE_COVERAGE)
        find_program(GCOVR_PATH gcov REQUIRED)
        find_program(GCOVR_PATH gcovr REQUIRED)

        target_compile_options(${target} PRIVATE "--coverage")
        target_link_libraries(${target} PRIVATE gcov)

        message(STATUS "Will generate Coverage for ${target}")
    endif()
endfunction()
