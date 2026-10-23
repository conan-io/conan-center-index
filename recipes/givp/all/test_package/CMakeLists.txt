# SPDX-FileCopyrightText: 2026 Arnaldo Mendes Pires Junior
# SPDX-License-Identifier: MIT

cmake_minimum_required(VERSION 3.21)
project(example LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(givp CONFIG REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE givp::givp)
