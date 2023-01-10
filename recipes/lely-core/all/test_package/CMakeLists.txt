cmake_minimum_required(VERSION 3.2)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(lely-core REQUIRED)
find_package(Threads REQUIRED)

add_executable("${PROJECT_NAME}" test_package.cpp)
target_link_libraries("${PROJECT_NAME}" PRIVATE lely-core::lely-core Threads::Threads)
target_compile_features("${PROJECT_NAME}" PRIVATE cxx_std_11)
