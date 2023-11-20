# Simplified version of https://github.com/connormanning/arbiter/blob/70b57eeddfaed426d8edc8a5f02c87defd3a0f22/CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(arbiter)

set(CMAKE_THREAD_PREFER_PTHREAD TRUE)

find_package(Threads REQUIRED)
find_package(CURL REQUIRED CONFIG)
find_package(OpenSSL REQUIRED CONFIG)
find_package(ZLIB REQUIRED CONFIG)
find_package(nlohmann_json REQUIRED CONFIG)
find_package(rapidxml REQUIRED CONFIG)

set(CMAKE_CXX_STANDARD 11)
if (${CMAKE_CXX_COMPILER_ID} STREQUAL GNU OR ${CMAKE_CXX_COMPILER_ID} STREQUAL Clang)
    add_definitions(-DUNIX)
    add_compile_options(-Wno-deprecated-declarations -Wall -pedantic -fexceptions)
elseif (${CMAKE_CXX_COMPILER_ID} STREQUAL MSVC)
    add_definitions(-DWINDOWS)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
    if(BUILD_SHARED_LIBS)
        add_definitions(-DARBITER_DLL_EXPORT)
    endif()
    link_libraries(Shlwapi)
endif()

file(GLOB_RECURSE ARBITER_SRC src/arbiter/*.cpp)
add_library(arbiter ${ARBITER_SRC})

target_include_directories(arbiter PRIVATE src)
target_compile_definitions(arbiter PRIVATE
    -DARBITER_OPENSSL
    -DARBITER_CURL
    -DARBITER_ZLIB
)
target_link_libraries(arbiter PRIVATE
    ZLIB::ZLIB
    CURL::libcurl
    Threads::Threads
    OpenSSL::SSL
    OpenSSL::Crypto
    nlohmann_json::nlohmann_json
    rapidxml::rapidxml
)

install(TARGETS arbiter
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)
