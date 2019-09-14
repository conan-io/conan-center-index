cmake_minimum_required(VERSION 3.5)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} 000-CatchMain.cpp 100-Fix-Section.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
