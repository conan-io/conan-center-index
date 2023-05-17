cmake_minimum_required(VERSION 3.12)
project(PackageTest CXX)

find_package(resource_pool REQUIRED)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example coro.cc)
target_compile_features(example PRIVATE cxx_std_17)
target_link_libraries(example PRIVATE elsid::resource_pool)
