cmake_minimum_required(VERSION 3.1)
project(test_package)

option(WITH_LIBSODIUM "zeromq is built with libsodium")

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(ZeroMQ REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# TODO: remove ZeroMQ:: namespace when fixed in conanfile.py
if(ZEROMQ_SHARED)
  target_link_libraries(${PROJECT_NAME} ZeroMQ::libzmq)
else()
  target_link_libraries(${PROJECT_NAME} ZeroMQ::libzmq-static)
endif()

if(WITH_LIBSODIUM)
  target_compile_definitions(${PROJECT_NAME} PRIVATE "WITH_LIBSODIUM")
endif()

if(WITH_NORM)
  target_compile_definitions(${PROJECT_NAME} PRIVATE "WITH_NORM")
endif()
