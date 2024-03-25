cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(embree REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.v${embree_VERSION_MAJOR}.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE embree)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
