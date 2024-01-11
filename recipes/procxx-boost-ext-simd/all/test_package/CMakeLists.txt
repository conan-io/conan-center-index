cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

# FIXME: components from Boost.SIMD (target Boost::SIMD) don't work.
# It should be:
# find_package(BOOST REQUIRED COMPONENTS SIMD)
# See https://github.com/conan-io/conan-center-index/issues/6682 for details.

find_package(Boost.SIMD REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Boost::headers Boost::SIMD)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
