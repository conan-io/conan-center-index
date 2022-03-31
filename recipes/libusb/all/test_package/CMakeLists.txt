cmake_minimum_required(VERSION 3.13)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if (APPLE)
    add_link_options(-framework Security)
endif(APPLE)

add_executable(${CMAKE_PROJECT_NAME} test_package.c)
target_link_libraries(${CMAKE_PROJECT_NAME} ${CONAN_LIBS})
