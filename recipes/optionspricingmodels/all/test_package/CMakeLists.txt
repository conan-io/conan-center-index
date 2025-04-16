cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(OptionsPricingModels REQUIRED)
find_package(GTest REQUIRED)

enable_testing()

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE OptionsPricingModels GTest::GTest GTest::Main)

include(GoogleTest)
gtest_discover_tests(test_package)
