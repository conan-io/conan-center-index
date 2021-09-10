cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

option(OPENSSL_WITH_ZLIB "OpenSSL with zlib support" ON)

set(OpenSSL_DEBUG 1)
find_package(OpenSSL REQUIRED)

message("OPENSSL_FOUND: ${OPENSSL_FOUND}")
message("OPENSSL_INCLUDE_DIR: ${OPENSSL_INCLUDE_DIR}")
message("OPENSSL_CRYPTO_LIBRARY: ${OPENSSL_CRYPTO_LIBRARY}")
message("OPENSSL_CRYPTO_LIBRARIES: ${OPENSSL_CRYPTO_LIBRARIES}")
message("OPENSSL_SSL_LIBRARY: ${OPENSSL_SSL_LIBRARY}")
message("OPENSSL_SSL_LIBRARIES: ${OPENSSL_SSL_LIBRARIES}")
message("OPENSSL_LIBRARIES: ${OPENSSL_LIBRARIES}")
message("OPENSSL_VERSION: ${OPENSSL_VERSION}")

add_executable(digest digest.c)
if(OPENSSL_WITH_ZLIB)
    target_compile_definitions(digest PRIVATE WITH_ZLIB)
endif()
target_link_libraries(digest OpenSSL::Crypto)
