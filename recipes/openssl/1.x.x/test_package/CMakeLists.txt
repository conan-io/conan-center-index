cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

option(OPENSSL_WITH_ZLIB "OpenSSL with zlib support" ON)

find_package(OpenSSL REQUIRED)

add_executable(digest digest.c)
target_link_libraries(digest OpenSSL::SSL)
if(OPENSSL_WITH_ZLIB)
    target_compile_definitions(digest PRIVATE WITH_ZLIB)
endif()
