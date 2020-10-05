cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(czmq REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# TODO: remove czmq:: namespace when fixed in conanfile.py
if(CZMQ_SHARED)
  target_link_libraries(${PROJECT_NAME} czmq::czmq)
else()
  target_link_libraries(${PROJECT_NAME} czmq::czmq-static)
endif()

if(WITH_LIBSODIUM)
  target_compile_definitions(${PROJECT_NAME} PRIVATE "WITH_LIBSODIUM")
endif()
