cmake_minimum_required(VERSION 3.0)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(zbar CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} zbar::zbar)

if ("${zbar_VERSION}" VERSION_GREATER_EQUAL "0.22")
    target_compile_definitions(${PROJECT_NAME} PRIVATE ZBAR_VERSION_PARAM3)
endif()
