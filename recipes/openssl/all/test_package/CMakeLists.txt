PROJECT(test_package)
cmake_minimum_required(VERSION 2.8)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(digest digest.cpp)

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

    add_executable(test_crypto test_crypto.cpp)
    target_link_libraries(test_crypto OpenSSL::Crypto)

    add_executable(test_crypto_bad EXCLUDE_FROM_ALL test_crypto.cpp)
    target_link_libraries(test_crypto OpenSSL::SSL)

    add_executable(test_ssl test_ssl.c)
    target_link_libraries(test_ssl OpenSSL::SSL)

    add_executable(test_ssl_bad EXCLUDE_FROM_ALL test_ssl.c)
    target_link_libraries(test_ssl OpenSSL::Crypto)
else()
    message("LINK WITH ${CONAN_LIBS}")
    target_include_directories(digest PRIVATE ${CONAN_INCLUDE_DIRS})
    target_link_libraries(digest PRIVATE ${CONAN_LIBS})
endif()
