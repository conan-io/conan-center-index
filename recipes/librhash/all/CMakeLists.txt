# Based on https://github.com/rhash/RHash/pull/103
cmake_minimum_required(VERSION 3.15)
project(librhash LANGUAGES C)

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/src/version.h" versionfile)
string(REGEX MATCH "#define VERSION \"([0-9]*)\.([0-9]*)\.([0-9]*)\"" _ ${versionfile})
set(RHASH_VERSION_MAJOR ${CMAKE_MATCH_1})
set(RHASH_VERSION_MINOR ${CMAKE_MATCH_2})
set(RHASH_VERSION_PATCH ${CMAKE_MATCH_3})
set(RHASH_VERSION "${RHASH_VERSION_MAJOR}.${RHASH_VERSION_MINOR}.${RHASH_VERSION_PATCH}")

option(USE_OPENSSL "Enable OpenSSL (optimized hash functions) support" ON)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

set(SRC_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/src/librhash")
file(GLOB SOURCE_FILES "${SRC_ROOT}/*.c")
file(GLOB HEADER_FILES "${SRC_ROOT}/*.h")

add_library(${PROJECT_NAME} ${SOURCE_FILES} ${HEADER_FILES})
set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME "${CMAKE_PROJECT_NAME}")

if(USE_OPENSSL)
    find_package(OpenSSL REQUIRED)
    target_link_libraries(${PROJECT_NAME} OpenSSL::Crypto)
    target_compile_definitions(${PROJECT_NAME} PUBLIC USE_OPENSSL)
endif()

if(MSVC)
    target_compile_definitions(${PROJECT_NAME} PRIVATE _CRT_SECURE_NO_DEPRECATE)
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES
                      COMPILE_DEFINITIONS IN_RHASH
                      DEFINE_SYMBOL RHASH_EXPORTS
                      PREFIX ""
                      IMPORT_PREFIX ""
                      VERSION ${RHASH_VERSION}
                      SOVERSION ${RHASH_VERSION_MAJOR})

install(TARGETS ${PROJECT_NAME}
       RUNTIME DESTINATION bin
       LIBRARY DESTINATION lib
       ARCHIVE DESTINATION lib)

install(FILES "${SRC_ROOT}/rhash.h" "${SRC_ROOT}/rhash_torrent.h"
        DESTINATION include)
