cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

if (NOT DEFINED ENV{LEX})
    message(FATAL_ERROR "LEX environment variable is not defined")
else()
    message(STATUS "LEX environment variable is set to: $ENV{LEX}")
endif()

if (NOT CMAKE_CROSSCOMPILING)
    find_package(FLEX REQUIRED)
    flex_target(flex_scanner basic_nr.l ${PROJECT_BINARY_DIR}/basic_nr.cpp)
    set(TEST_PACKAGE_SOURCES ${PROJECT_BINARY_DIR}/basic_nr.cpp)
else()
    # When cross-building, will find an executable that we can't run, but won't error
    # (it is useful to find the library)
    find_package(FLEX)
    set(TEST_PACKAGE_SOURCES test_package_crossbuild.cpp)
endif()

if (NOT FLEX_FOUND)
    message(FATAL_ERROR "FLEX not found!")
endif()

# From https://gitlab.kitware.com/cmake/cmake/-/blame/master/Modules/FindFLEX.cmake#L236
if(FLEX_FOUND AND NOT TARGET FLEX::fl)
add_library(FLEX::fl INTERFACE IMPORTED)
set_target_properties(
    FLEX::fl
    PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${FLEX_INCLUDE_DIRS}"
    INTERFACE_LINK_LIBRARIES "${FLEX_LIBRARIES}"
)
endif()

add_executable(${PROJECT_NAME} ${TEST_PACKAGE_SOURCES})
target_link_libraries(${PROJECT_NAME} PRIVATE FLEX::fl)
