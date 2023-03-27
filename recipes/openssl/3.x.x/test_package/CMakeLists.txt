cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

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
    if(DEFINED ${_custom_var})
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()

add_executable(test_package test_package.c digest.c)
target_link_libraries(test_package PRIVATE OpenSSL::SSL OpenSSL::Crypto)

if(OPENSSL_WITH_LEGACY)
    target_sources(test_package PRIVATE digest_legacy.c)
    # do now show deperecation warnings
    target_compile_definitions(test_package PRIVATE OPENSSL_SUPPRESS_DEPRECATED TEST_OPENSSL_LEGACY)
    if(OPENSSL_WITH_MD4)
      target_compile_definitions(test_package PRIVATE OPENSSL_WITH_MD4)
    endif()
    if(OPENSSL_WITH_RIPEMD160)
      target_compile_definitions(test_package PRIVATE OPENSSL_WITH_RIPEMD160)
    endif()
endif()
