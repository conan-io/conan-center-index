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
    message("LINK WITH ${OpenSSL_LIBRARIES}")

    target_link_libraries(digest OpenSSL::SSL)
else()
    message("LINK WITH ${CONAN_LIBS}")
    target_include_directories(digest PRIVATE ${CONAN_INCLUDE_DIRS})
    target_link_libraries(digest PRIVATE ${CONAN_LIBS})
endif()
