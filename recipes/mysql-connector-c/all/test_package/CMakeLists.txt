cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Threads)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS} ${CMAKE_DL_LIBS} ${CMAKE_THREAD_LIBS_INIT})
