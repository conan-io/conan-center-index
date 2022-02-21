cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(xapian REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_include_directories(${PROJECT_NAME} PRIVATE ${XAPIAN_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME} ${XAPIAN_LIBRARIES})
