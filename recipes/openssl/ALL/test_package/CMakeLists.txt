cmake_minimum_required(VERSION 2.8)
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
    message("LINK WITH ${OPENSSL_LIBRARIES}")

    target_include_directories(digest PRIVATE ${OPENSSL_INCLUDE_DIRS})
    target_link_libraries(digest ${OPENSSL_LIBRARIES})

    find_package(Threads)
    target_link_libraries(digest PRIVATE ${CMAKE_THREAD_LIBS_INIT})

    if(WIN32)
        target_link_libraries(digest PRIVATE ws2_32 crypt32)
    endif()
    if(UNIX AND NOT APPLE)
        target_link_libraries(digest PRIVATE ${CMAKE_DL_LIBS})
    endif()
else()
    message("LINK WITH ${CONAN_LIBS}")
    target_include_directories(digest PRIVATE ${CONAN_INCLUDE_DIRS})
    target_link_libraries(digest PRIVATE ${CONAN_LIBS})
endif()
