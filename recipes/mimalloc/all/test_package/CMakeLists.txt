cmake_minimum_required(VERSION 2.8.11)
project(PackageTest C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

option(BUILD_BASIC           "Build test_basic" OFF)
option(BUILD_REDEFINE_MALLOC "Build test_redefine_malloc" OFF)

if (BUILD_BASIC)
    add_executable(test_basic test_basic.c)
    target_link_libraries(test_basic ${CONAN_LIBS})

    add_executable(test_basic_cpp test_basic.cpp)
    target_link_libraries(test_basic_cpp ${CONAN_LIBS})
endif (BUILD_BASIC)

if (BUILD_REDEFINE_MALLOC)
    add_executable(test_redefine_malloc test_redefine_malloc.c)
    target_link_libraries(test_redefine_malloc ${CONAN_LIBS})
endif (BUILD_REDEFINE_MALLOC)
