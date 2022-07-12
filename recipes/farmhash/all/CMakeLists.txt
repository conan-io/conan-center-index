cmake_minimum_required(VERSION 3.4)
project(farmhash CXX)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(FARMHASH_SOURCE_DIR source_subfolder)

if (NOT FARMHASH_NO_BUILTIN_EXPECT)
    # Transcribed from farmhash/src/Makefile.am
    include(CheckCXXSourceCompiles)
    check_cxx_source_compiles(
        "int main(int argc, char* argv[]) { return (int)__builtin_expect(0, 0); }"
        FARMHASH_HAS_BUILTIN_EXPECT
    )
endif()

add_library(farmhash "${FARMHASH_SOURCE_DIR}/src/farmhash.cc" )
target_include_directories(farmhash PRIVATE "${FARMHASH_SOURCE_DIR}/src")

if(NOT FARMHASH_HAS_BUILTIN_EXPECT)
  target_compile_definitions(farmhash PUBLIC -DFARMHASH_NO_BUILTIN_EXPECT)
endif()

set_target_properties(farmhash
    PROPERTIES
    PUBLIC_HEADER "${FARMHASH_SOURCE_DIR}/src/farmhash.h"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

install (TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)
