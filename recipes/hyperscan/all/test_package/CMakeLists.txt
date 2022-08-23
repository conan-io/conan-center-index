cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(hyperscan COMPONENTS hs REQUIRED)
add_executable(hs_example hs_example.cpp)
target_link_libraries(hs_example PRIVATE hyperscan::hs)

if(BUILD_CHIMERA)
    find_package(hyperscan COMPONENTS chimera REQUIRED)
    add_executable(ch_example ch_example.cpp)
    target_link_libraries(ch_example PRIVATE hyperscan::chimera)
endif()

