cmake_minimum_required(VERSION 3.1)
project(mongo-c-driver-tester C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} tester.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
