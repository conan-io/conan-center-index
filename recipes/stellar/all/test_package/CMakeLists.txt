cmake_minimum_required(VERSION 3.25)
project(stellar_test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(stellar CONFIG REQUIRED)

add_executable(stellar_smoke src/smoke.cpp)
target_link_libraries(stellar_smoke PRIVATE stellar::stellar)
