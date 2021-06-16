cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(PkgConfig REQUIRED)
pkg_check_modules(BREAKPAD REQUIRED IMPORTED_TARGET breakpad-client)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::BREAKPAD)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
