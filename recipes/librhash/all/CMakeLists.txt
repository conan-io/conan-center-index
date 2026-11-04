# Based on https://github.com/rhash/RHash/pull/103
cmake_minimum_required(VERSION 3.15)
project(rhash LANGUAGES C)

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/../version.h" versionfile)
string(REGEX MATCH "#define VERSION \"([0-9]*)\.([0-9]*)\.([0-9]*)\"" _ ${versionfile})
set(RHASH_VERSION_MAJOR ${CMAKE_MATCH_1})
set(RHASH_VERSION_MINOR ${CMAKE_MATCH_2})
set(RHASH_VERSION_PATCH ${CMAKE_MATCH_3})
set(RHASH_VERSION "${RHASH_VERSION_MAJOR}.${RHASH_VERSION_MINOR}.${RHASH_VERSION_PATCH}")

option(USE_OPENSSL "Enable OpenSSL (optimized hash functions) support" ON)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

# Get the list of source files from the Makefile
# https://github.com/rhash/RHash/blob/v1.4.4/librhash/Makefile#L6
file(READ Makefile MAKEFILE_CONTENTS)
if("${MAKEFILE_CONTENTS}" MATCHES "SOURCES *= *([^\n]+)")
    string(REPLACE " " ";" SOURCE_FILES ${CMAKE_MATCH_1})
else()
    message(FATAL_ERROR "SOURCES line not found in Makefile")
endif()

add_library(rhash ${SOURCE_FILES})

if(USE_OPENSSL)
    find_package(OpenSSL REQUIRED)
    target_link_libraries(rhash OpenSSL::Crypto)
    target_compile_definitions(rhash PUBLIC USE_OPENSSL)
endif()

if(MSVC)
    target_compile_definitions(rhash PRIVATE _CRT_SECURE_NO_DEPRECATE)
endif()

set_target_properties(rhash PROPERTIES
                      COMPILE_DEFINITIONS IN_RHASH
                      DEFINE_SYMBOL RHASH_EXPORTS
                      VERSION ${RHASH_VERSION}
                      SOVERSION ${RHASH_VERSION_MAJOR})

install(TARGETS rhash
       RUNTIME DESTINATION bin
       LIBRARY DESTINATION lib
       ARCHIVE DESTINATION lib)

install(FILES "rhash.h" "rhash_torrent.h" DESTINATION include)
