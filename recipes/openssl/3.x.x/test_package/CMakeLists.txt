cmake_minimum_required(VERSION 2.8.11)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

option(OPENSSL_WITH_ZLIB "OpenSSL with zlib support" ON)

add_executable(digest digest.cpp)
if(OPENSSL_WITH_ZLIB)
    target_compile_definitions(digest PRIVATE WITH_ZLIB)
endif()

message("LINK WITH ${CONAN_LIBS}")
target_include_directories(digest PRIVATE ${CONAN_INCLUDE_DIRS})
target_link_libraries(digest PRIVATE ${CONAN_LIBS})
