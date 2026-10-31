cmake_minimum_required(VERSION 3.14)
project(test_constest_with_conan)

set(CMAKE_CXX_STANDARD 20)

find_package(constest REQUIRED CONFIG)
find_package(GTest REQUIRED CONFIG)

add_executable(test_constest_with_conan test.cpp)
target_link_libraries(test_constest_with_conan PRIVATE constest::constest GTest::gtest_main)
target_compile_definitions(test_constest_with_conan PRIVATE CONSTEST_CONFIG_GTEST)
