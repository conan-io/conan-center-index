# SPDX-License-Identifier: MIT Copyright (c) 2022 Jai Bellare See
# <https://opensource.org/licenses/MIT/> or LICENSE.md Project homepage:
# <https://github.com/strangeQuark1041/samarium>

cmake_minimum_required(VERSION 3.16)
project(samarium_dev LANGUAGES CXX)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

include(modern_project_structure)
include(ubsan)
include(conan_install)
include(ccache)
include(compiler_options)
include(docs)

add_subdirectory(src)

include(CTest)
enable_testing()
add_subdirectory(test)
add_test(NAME SamariumTests COMMAND samarium_tests)

option(GENERATE_COVERAGE "Generate coverage reports" FALSE)
include(coverage)
generate_coverage(samarium_tests)

option(USE_IWYU "Use include what you use" FALSE)
include(include_what_you_use)
iwyu(samarium_tests)
