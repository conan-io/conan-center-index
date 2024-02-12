cmake_minimum_required(VERSION 3.8)
project(test_package C)

option(OPENSSL_WITH_ZLIB "OpenSSL with zlib support" ON)

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

add_executable(${PROJECT_NAME} digest.c)
target_link_libraries(${PROJECT_NAME} PRIVATE OpenSSL::SSL)
target_compile_definitions(${PROJECT_NAME} PRIVATE $<$<BOOL:${OPENSSL_WITH_ZLIB}>:WITH_ZLIB>)
