PROJECT(MyHello)
cmake_minimum_required(VERSION 2.8)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

ADD_EXECUTABLE(digest digest.cpp)

if(USE_FIND_PACKAGE)
    set(OpenSSL_DEBUG 1)
    find_package(OpenSSL REQUIRED)
    MESSAGE("LINK WITH ${OPENSSL_LIBRARIES}")

    target_include_directories(digest PRIVATE ${OPENSSL_INCLUDE_DIRS})
    TARGET_LINK_LIBRARIES(digest ${OPENSSL_LIBRARIES})

    find_package(Threads)
    target_link_libraries(digest PRIVATE ${CMAKE_THREAD_LIBS_INIT})

    if(WIN32)
        TARGET_LINK_LIBRARIES(digest PRIVATE ws2_32 crypt32)
    endif()
    if(UNIX AND NOT APPLE)
        TARGET_LINK_LIBRARIES(digest PRIVATE ${CMAKE_DL_LIBS})
    endif()
else()
    MESSAGE("LINK WITH ${CONAN_LIBS}")
    target_include_directories(digest PRIVATE ${CONAN_INCLUDE_DIRS})
    TARGET_LINK_LIBRARIES(digest PRIVATE ${CONAN_LIBS})
endif()
