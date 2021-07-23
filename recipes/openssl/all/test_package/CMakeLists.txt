cmake_minimum_required(VERSION 3.1)
project(OpenSSLTests)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

option(OPENSSL_WITH_ZLIB "OpenSSL with zlib support" ON)

add_executable(digest digest.cpp)
if(OPENSSL_WITH_ZLIB)
    target_compile_definitions(digest PRIVATE WITH_ZLIB)
endif()


if(USE_FIND_PACKAGE)
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

    target_link_libraries(digest OpenSSL::SSL)
else()
    message("LINK WITH ${CONAN_LIBS}")
    target_include_directories(digest PRIVATE ${CONAN_INCLUDE_DIRS})
    target_link_libraries(digest PRIVATE ${CONAN_LIBS})
endif()
