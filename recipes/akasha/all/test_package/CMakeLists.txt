cmake_minimum_required(VERSION 3.16)
project(TestPackageAkasha CXX)

find_package(akasha REQUIRED)

add_executable(test_akasha test.cpp)
target_link_libraries(test_akasha PRIVATE akasha::akasha)
