cmake_minimum_required(VERSION 3.30.5)
project(test_package LANGUAGES CXX)

message(STATUS "MP_UNITS_BUILD_CXX_MODULES: ${MP_UNITS_BUILD_CXX_MODULES}")

find_package(mp-units REQUIRED)

add_executable(test_package-headers test_package.cpp)
target_compile_features(test_package-headers PRIVATE $<IF:$<BOOL:${CMAKE_CXX_MODULE_STD}>,cxx_std_23,cxx_std_20>)
target_link_libraries(test_package-headers PRIVATE mp-units::mp-units)
