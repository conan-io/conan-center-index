cmake_minimum_required(VERSION 2.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${CMAKE_PROJECT_NAME} test_package.c)
target_link_libraries(${CMAKE_PROJECT_NAME} ${CONAN_LIBS})
