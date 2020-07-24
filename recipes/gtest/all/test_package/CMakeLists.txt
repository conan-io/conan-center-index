cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(GTest REQUIRED)

if(WITH_MAIN)
    add_executable(${PROJECT_NAME} test_package.cpp)
else()
    add_executable(${PROJECT_NAME} main.cpp test_package.cpp)
endif()

target_link_libraries(${PROJECT_NAME} GTest::gtest GTest::gtest_main GTest::gmock GTest::gmock_main)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
if(WITH_GMOCK)
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_GMOCK)
endif()
