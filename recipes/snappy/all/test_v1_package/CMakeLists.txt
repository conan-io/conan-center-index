cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Snappy REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Snappy::snappy)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

add_executable(${PROJECT_NAME}_c ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE Snappy::snappy)
