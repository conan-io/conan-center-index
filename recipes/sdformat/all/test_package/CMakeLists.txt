cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(SDFORMAT_MAJOR_VER 10)

find_package(sdformat${SDFORMAT_MAJOR_VER} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} sdformat${SDFORMAT_MAJOR_VER}::sdformat${SDFORMAT_MAJOR_VER})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
