cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

function(SetCompilerOptions target ac_version)
    if(ac_version GREATER "26")
        target_compile_features("${target}" PUBLIC cxx_std_17)
    else()
        target_compile_features("${target}" PUBLIC cxx_std_14)
    endif()

    target_compile_definitions("${target}" PUBLIC "\$<\$<CONFIG:Debug>:DEBUG>")

    if(WIN32)
        target_compile_options(
            "${target}" PRIVATE
            /W4 /WX
            /Zc:wchar_t-
            /wd4499
            /EHsc
        )
    else()
        target_compile_options(
            "${target}" PRIVATE
            -Wall -Wextra -Werror
            -fvisibility=hidden
            -Wno-multichar
            -Wno-ctor-dtor-privacy
            -Wno-invalid-offsetof
            -Wno-ignored-qualifiers
            -Wno-reorder
            -Wno-overloaded-virtual
            -Wno-unused-parameter
            -Wno-deprecated
        )
    endif()
endfunction()

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS KEEP_RPATHS)

set(AC_API_DEVKIT_DIR "${CONAN_ARCHICAD-APIDEVKIT_ROOT}/bin" CACHE PATH "API DevKit directory.")
find_package(archicad-apidevkit REQUIRED CONFIG)

add_executable(test_package ../test_package/test_gsroot.cpp)
SetCompilerOptions(test_package "${archicad-apidevkit_VERSION}")

if(WIN32)
    target_compile_definitions(test_package PRIVATE UNICODE _UNICODE)
else()
    target_compile_definitions(test_package PRIVATE macintosh=1)
endif()

target_include_directories(test_package SYSTEM PRIVATE "${AC_API_DEVKIT_DIR}/Modules/GSRoot")

if(WIN32)
    target_link_libraries(
        test_package PRIVATE
        "${AC_API_DEVKIT_DIR}/Modules/GSRoot/Win/GSRootImp.lib"
    )
else()
    find_library(
        GSROOT_FRAMEWORK GSRoot
        PATHS "${AC_API_DEVKIT_DIR}/Frameworks"
    )

    if(NOT GSROOT_FRAMEWORK)
        message(FATAL_ERROR "GSRoot not found: ${GSROOT_FRAMEWORK}")
    endif()

    target_link_libraries(test_package PRIVATE "${GSROOT_FRAMEWORK}")
endif()
