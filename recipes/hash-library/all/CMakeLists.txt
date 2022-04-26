cmake_minimum_required(VERSION 3.4)
project(hash-library CXX)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_library(${CMAKE_PROJECT_NAME}
    source_subfolder/crc32.cpp
    source_subfolder/keccak.cpp
    source_subfolder/md5.cpp
    source_subfolder/sha1.cpp
    source_subfolder/sha256.cpp
    source_subfolder/sha3.cpp
)

target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE source_subfolder)

set(HEADERS
    source_subfolder/crc32.h
    source_subfolder/hash.h
    source_subfolder/hmac.h
    source_subfolder/keccak.h
    source_subfolder/md5.h
    source_subfolder/sha1.h
    source_subfolder/sha256.h
    source_subfolder/sha3.h
)

set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES 
    PUBLIC_HEADER "${HEADERS}"
)

install(TARGETS ${CMAKE_PROJECT_NAME}
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)
