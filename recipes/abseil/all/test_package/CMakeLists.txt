cmake_minimum_required(VERSION 3.1.0)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# Test components
find_package(absl REQUIRED)
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} absl::strings absl::flat_hash_map absl::flat_hash_set absl::int128 absl::time)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

# Test also global target
add_executable(${PROJECT_NAME}_global test_package.cpp)
target_link_libraries(${PROJECT_NAME}_global CONAN_PKG::abseil)
set_property(TARGET ${PROJECT_NAME}_global PROPERTY CXX_STANDARD 11)
