cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Fontconfig REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} Fontconfig::Fontconfig)
set_target_properties(${PROJECT_NAME} PROPERTIES C_STANDARD 99)

