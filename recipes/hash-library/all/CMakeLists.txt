cmake_minimum_required(VERSION 3.4)
project(hash-library LANGUAGES CXX)

add_library(hash-library
    ${HASH_LIBRARY_SRC_DIR}/crc32.cpp
    ${HASH_LIBRARY_SRC_DIR}/keccak.cpp
    ${HASH_LIBRARY_SRC_DIR}/md5.cpp
    ${HASH_LIBRARY_SRC_DIR}/sha1.cpp
    ${HASH_LIBRARY_SRC_DIR}/sha256.cpp
    ${HASH_LIBRARY_SRC_DIR}/sha3.cpp
)

target_include_directories(hash-library PUBLIC ${HASH_LIBRARY_SRC_DIR})

set(HEADERS
    ${HASH_LIBRARY_SRC_DIR}/crc32.h
    ${HASH_LIBRARY_SRC_DIR}/hash.h
    ${HASH_LIBRARY_SRC_DIR}/hmac.h
    ${HASH_LIBRARY_SRC_DIR}/keccak.h
    ${HASH_LIBRARY_SRC_DIR}/md5.h
    ${HASH_LIBRARY_SRC_DIR}/sha1.h
    ${HASH_LIBRARY_SRC_DIR}/sha256.h
    ${HASH_LIBRARY_SRC_DIR}/sha3.h
)

set_target_properties(hash-library PROPERTIES
    PUBLIC_HEADER "${HEADERS}"
    WINDOWS_EXPORT_ALL_SYMBOLS TRUE
)

include(GNUInstallDirs)
install(TARGETS hash-library
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
