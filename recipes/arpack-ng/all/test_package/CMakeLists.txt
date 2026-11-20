cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(arpackng REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE ARPACK::ARPACK)

add_executable(test_package_eigen test_package_eigen.cpp)
target_link_libraries(test_package_eigen PRIVATE ARPACK::ARPACK)
target_compile_features(test_package_eigen PRIVATE cxx_std_14)
