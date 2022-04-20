cmake_minimum_required(VERSION 3.1)
project(test_package C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Sail REQUIRED CONFIG)

# C API
add_executable(test_package_c test_package.c)
target_compile_definitions(test_package_c PRIVATE SAIL_DEMO_FILE_PATH="${CMAKE_CURRENT_SOURCE_DIR}/png.png")
target_link_libraries(test_package_c PRIVATE SAIL::Sail)

# C++ API
add_executable(test_package_cxx test_package.cpp)
target_compile_definitions(test_package_cxx PRIVATE SAIL_DEMO_FILE_PATH="${CMAKE_CURRENT_SOURCE_DIR}/png.png")
target_link_libraries(test_package_cxx PRIVATE SAIL::SailC++)
