cmake_minimum_required(VERSION 3.1.0)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(absl REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} absl::strings absl::flat_hash_map absl::flat_hash_set absl::int128 absl::time)
