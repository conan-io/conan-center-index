cmake_minimum_required(VERSION 3.4)
project(farmhash LANGUAGES CXX)

include(GNUInstallDirs)

if(NOT FARMHASH_NO_BUILTIN_EXPECT)
    # Transcribed from farmhash/src/Makefile.am
    include(CheckCXXSourceCompiles)
    check_cxx_source_compiles(
        "int main(int argc, char* argv[]) { return (int)__builtin_expect(0, 0); }"
        FARMHASH_HAS_BUILTIN_EXPECT
    )
endif()

add_library(farmhash "${FARMHASH_SRC_DIR}/src/farmhash.cc" )
target_include_directories(farmhash PRIVATE "${FARMHASH_SRC_DIR}/src")

if(NOT FARMHASH_HAS_BUILTIN_EXPECT)
    target_compile_definitions(farmhash PUBLIC FARMHASH_NO_BUILTIN_EXPECT)
endif()

set_target_properties(farmhash
    PROPERTIES
        PUBLIC_HEADER "${FARMHASH_SRC_DIR}/src/farmhash.h"
        WINDOWS_EXPORT_ALL_SYMBOLS ON
)

install(TARGETS farmhash
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
