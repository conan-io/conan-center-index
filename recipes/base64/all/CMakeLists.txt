# Written in 2016-2017 by Henrik Steffen Gaßmann henrik@gassmann.onl
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication
# along with this software. If not, see
#
#     http://creativecommons.org/publicdomain/zero/1.0/
#
########################################################################
cmake_minimum_required(VERSION 3.1)

project(base64 LANGUAGES C VERSION 0.3.0)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/Modules")

#######################################################################
# platform detection
include(TargetArch)
detect_target_architecture(_TARGET_ARCH)


########################################################################
# Compilation options
option(BASE64_INSTALL_TARGET "add an install target" ON)
option(BASE64_BUILD_TESTS "add test projects" ON)
option(BASE64_WITH_OPENMP "use openmp" OFF)

if (_TARGET_ARCH STREQUAL "x86" OR _TARGET_ARCH STREQUAL "x64")
    option(BASE64_WITH_FAST_UNALIGNED_ACCESS "vectorization: unaligned access enabled" ON)
    option(BASE64_WITH_SSSE3 "add SSSE 3 codepath" ON)
    option(BASE64_WITH_SSE41 "add SSE 4.1 codepath" ON)
    option(BASE64_WITH_SSE42 "add SSE 4.2 codepath" ON)
    option(BASE64_WITH_AVX "add AVX codepath" ON)
    option(BASE64_WITH_AVX2 "add AVX 2 codepath" ON)

elseif (_TARGET_ARCH STREQUAL "arm")
    option(BASE64_WITH_NEON32 "add NEON32 codepath" OFF)

elseif (_TARGET_ARCH STREQUAL "arm64")
    option(BASE64_WITH_NEON64 "add NEON64 codepath" ON)

endif()

###################################################################
# OpenMP
if(BASE64_WITH_OPENMP)
    find_package(OpenMP)
    if (OPENMP_FOUND)
        option(BASE64_USE_OpenMP "Utilize OpenMP to parallelize encoding and decoding." ON)
    endif()
endif()

########################################################################
# library project
add_library(base64 STATIC
    # library files
    lib/lib.c
    lib/codec_choose.c
    include/libbase64.h

    # codec implementations
    lib/arch/generic/codec.c

    lib/arch/ssse3/codec.c
    lib/arch/sse41/codec.c
    lib/arch/sse42/codec.c
    lib/arch/avx/codec.c
    lib/arch/avx2/codec.c

    lib/arch/neon32/codec.c
    lib/arch/neon64/codec.c
)

if (NOT BASE64_STANDALONE_PROJECT)
    # export inlucde path if base64 added as subdirectory
    target_include_directories(base64 INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    )
endif()

####################################################################
# platform/compiler specific configuration
set_target_properties(base64 PROPERTIES
    C_STANDARD 99
    C_STANDARD_REQUIRED YES
    C_EXTENSIONS OFF
)

target_compile_options(base64 PRIVATE
  $<$<C_COMPILER_ID:MSVC>:
    /W4
    /WX # All warnings as error
    /we4013 # Error warning C4013: 'function' undefined; assuming extern returning int
    /we4700 # Error warning C4700: uninitialized local variable
    /we4715 # not all control paths return a value
    /we4003 # not enough actual parameters for macro
    /wd4456 # disable warning C4456: declaration of 'xxx' hides previous local declaration
  >
  $<$<NOT:$<C_COMPILER_ID:MSVC>>:
    -Wall
    -Wextra
    -Wpedantic
  >
)

target_compile_definitions(base64 PRIVATE
  $<$<C_COMPILER_ID:MSVC>:
    # remove unnecessary warnings about unchecked iterators
    _SCL_SECURE_NO_WARNINGS
  >
)

########################################################################
# SIMD settings
include(TargetSIMDInstructionSet)
define_SIMD_compile_flags()

if (_TARGET_ARCH STREQUAL "x86" OR _TARGET_ARCH STREQUAL "x64")
    macro(configure_codec _TYPE)
        if (BASE64_WITH_${_TYPE})
            message(STATUS "Add codec: lib/arch/${_DIR}/codec.c")
            string(TOLOWER "${_TYPE}" _DIR)
            set_source_files_properties("lib/arch/${_DIR}/codec.c" PROPERTIES
                COMPILE_FLAGS "${COMPILE_FLAGS_${_TYPE}}"
            )

            if (${ARGC} GREATER 1 AND MSVC)
                set_source_files_properties("lib/arch/${_DIR}/codec.c" PROPERTIES
                    COMPILE_DEFINITIONS ${ARGV1}
                )
            endif()
        endif()
    endmacro()

    configure_codec(SSSE3 __SSSE3__)
    configure_codec(SSE41 __SSSE4_1__)
    configure_codec(SSE42 __SSSE4_2__)
    configure_codec(AVX)
    configure_codec(AVX2)

elseif (_TARGET_ARCH STREQUAL "arm")
    set(BASE64_NEON32_CFLAGS "${COMPILE_FLAGS_NEON32}" CACHE STRING "the NEON32 compile flags (for 'lib/arch/neon32/codec.c')")
    mark_as_advanced(BASE64_NEON32_CFLAGS)

    if (BASE64_WITH_NEON32)
        set_source_files_properties("lib/arch/neon32/codec.c" PROPERTIES
            COMPILE_FLAGS "${BASE64_NEON32_CFLAGS} "
        )
    endif()

#elseif (_TARGET_ARCH STREQUAL "arm64" AND BASE64_WITH_NEON64)

endif()

configure_file("${CMAKE_CURRENT_LIST_DIR}/cmake/config.h.in" "${CMAKE_CURRENT_BINARY_DIR}/config.h" @ONLY)
target_include_directories(base64 PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")

########################################################################
# OpenMP Settings
if (BASE64_USE_OpenMP)
    target_compile_options(base64
        PRIVATE
            ${OpenMP_C_FLAGS}
    )
endif()

########################################################################
if (BASE64_BUILD_TESTS)
    enable_testing()
    add_subdirectory(test)
endif()

########################################################################
# install target
if (BASE64_INSTALL_TARGET)
    install(TARGETS base64 EXPORT base64-targets
        RUNTIME DESTINATION bin/$<CONFIG>
        LIBRARY DESTINATION lib/$<CONFIG>
        ARCHIVE DESTINATION lib/$<CONFIG>
        INCLUDES DESTINATION include
    )
    install(FILES include/libbase64.h DESTINATION include)

    include(CMakePackageConfigHelpers)
    write_basic_package_version_file(
        "${CMAKE_CURRENT_BINARY_DIR}/base64-config-version.cmake"
        VERSION ${BASE64_VERSION}
        COMPATIBILITY ExactVersion
    )
    install(FILES "${CMAKE_CURRENT_BINARY_DIR}/base64-config-version.cmake" DESTINATION cmake)

    configure_file(cmake/base64-config.cmake
        "${CMAKE_CURRENT_BINARY_DIR}/base64-config.cmake"
        COPYONLY
    )
    install(FILES "${CMAKE_CURRENT_BINARY_DIR}/base64-config.cmake" DESTINATION cmake)

    install(EXPORT base64-targets DESTINATION cmake)
endif()
