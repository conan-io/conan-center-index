cmake_minimum_required(VERSION 3.10.2)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(IGN_MATH_MAJOR_VER 6)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(ignition-math${IGN_MATH_MAJOR_VER} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ignition-math${IGN_MATH_MAJOR_VER}::ignition-math${IGN_MATH_MAJOR_VER})

# When using clang in Linux with libc++, it seems that we need to explicitly link "libc++"
if (CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    string(FIND CMAKE_EXE_LINKER_FLAGS "-stdlib=libc++" LIBCPP)
    if (NOT ${LIBCPP} EQUAL -1)
        target_link_libraries(${PROJECT_NAME} "c++")
    endif()
endif()

