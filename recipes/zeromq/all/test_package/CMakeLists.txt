cmake_minimum_required(VERSION 2.8.12)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

find_package(ZeroMQ REQUIRED)
if(NOT TARGET libzmq OR NOT TARGET libzmq-static)
    message(FATAL_ERROR "No target libzmq or libzmq-static created")
endif()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

if(WITH_LIBSODIUM)
  target_compile_definitions(${PROJECT_NAME} PRIVATE "WITH_LIBSODIUM")
endif()
