cmake_minimum_required(VERSION 3.1)
project(test_package C)

option(OPENSSL_WITH_ZLIB "OpenSSL with zlib support" ON)
option(TRANSITIVE_ZLIB_HEADERS "Headers of the (transitive) ZLIB will be visible for test package" ON)
option(OPENSSL_WITH_LEGACY "OpenSSL with support for the legacy provider" ON)
option(OPENSSL_WITH_MD4 "OpenSSL with MD4 support (needs legacy provider)" ON)
option(OPENSSL_WITH_RIPEMD160 "OpenSSL with RIPEMD16 support (needs legacy provider)" ON)

set(OpenSSL_DEBUG 1)
find_package(OpenSSL REQUIRED)

# Test whether variables from https://cmake.org/cmake/help/latest/module/FindOpenSSL.html
# are properly defined in conan generators
set(_custom_vars
    OPENSSL_FOUND
    OPENSSL_INCLUDE_DIR
    OPENSSL_CRYPTO_LIBRARY
    OPENSSL_CRYPTO_LIBRARIES
    OPENSSL_SSL_LIBRARY
    OPENSSL_SSL_LIBRARIES
    OPENSSL_LIBRARIES
    OPENSSL_VERSION
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED ${_custom_var} AND NOT "${${_custom_var}}" STREQUAL "" )
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()

add_executable(digest digest.c)
if(OPENSSL_WITH_ZLIB AND TRANSITIVE_ZLIB_HEADERS)
    target_compile_definitions(digest PRIVATE WITH_ZLIB_HEADERS)
endif()
target_link_libraries(digest OpenSSL::Crypto)

if(OPENSSL_WITH_LEGACY)
    add_executable(digest_legacy digest_legacy.c)
    # do now show deperecation warnings
    target_compile_definitions(digest_legacy PRIVATE OPENSSL_SUPPRESS_DEPRECATED)
    if(OPENSSL_WITH_MD4)
      target_compile_definitions(digest_legacy PRIVATE OPENSSL_WITH_MD4)
    endif()
    if(OPENSSL_WITH_RIPEMD160)
      target_compile_definitions(digest_legacy PRIVATE OPENSSL_WITH_RIPEMD160)
    endif()
    if(OPENSSL_WITH_ZLIB)
        target_compile_definitions(digest_legacy PRIVATE WITH_ZLIB)
    endif()
    target_link_libraries(digest_legacy OpenSSL::Crypto)
endif()
