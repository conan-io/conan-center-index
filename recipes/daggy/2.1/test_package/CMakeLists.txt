cmake_minimum_required(VERSION 3.18.0)
project(DaggyPackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(daggy REQUIRED)

if (NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(testcpp test.cpp)
target_link_libraries(testcpp daggy::daggy)
