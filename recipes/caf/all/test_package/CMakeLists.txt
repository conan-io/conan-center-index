cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(CAF REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} CAF::core CAF::io CAF::openssl)
if (CAF_INIT_GLOBAL)
    target_compile_definitions(${PROJECT_NAME} PRIVATE INIT_GLOBAL)
endif()
