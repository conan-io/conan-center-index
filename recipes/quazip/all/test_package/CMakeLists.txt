cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(QuaZip-Qt5 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE QuaZip::QuaZip)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
# Must compile with "-fPIC" since Qt was built with -reduce-relocations.
target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)
