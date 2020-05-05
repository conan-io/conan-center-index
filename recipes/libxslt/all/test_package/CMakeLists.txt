cmake_minimum_required(VERSION 2.8.12)
project(libxslt_tutorial)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} libxslt_tutorial.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
