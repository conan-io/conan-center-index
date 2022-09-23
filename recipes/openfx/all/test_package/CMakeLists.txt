cmake_minimum_required(VERSION 3.1)
project(test_package)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_definitions(-D_HAS_AUTO_PTR_ETC)

# Conan
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
find_package(openfx REQUIRED CONFIG)

# Flags
if(MSVC)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DWINDOWS -DNOMINMAX")
else()
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wno-deprecated -Wno-deprecated-declarations")
endif()

# Build
add_executable(test_package invert.cpp)
target_link_libraries(test_package openfx::openfx)
