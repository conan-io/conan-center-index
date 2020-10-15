cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/example.ttf
     DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

add_executable(${CMAKE_PROJECT_NAME} example.c)
target_link_libraries(${CMAKE_PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY C_STANDARD 99)
