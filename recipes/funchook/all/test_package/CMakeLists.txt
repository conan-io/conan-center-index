cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES C ASM)

find_package(funchook REQUIRED CONFIG)

set(FUNCHOOK_CPU ${CMAKE_SYSTEM_PROCESSOR})

if (FUNCHOOK_CPU STREQUAL AMD64)
    set(FUNCHOOK_CPU "x86_64")
endif ()

if (FUNCHOOK_CPU STREQUAL x86_64)
    if (CMAKE_SIZEOF_VOID_P EQUAL "4")
        set(FUNCHOOK_CPU "x86")
    endif ()
endif ()

if (FUNCHOOK_CPU MATCHES "i.86")
    set(FUNCHOOK_CPU "x86")
endif ()

set(TEST_EXE_SOURCES test_main.c)
if (FUNCHOOK_CPU STREQUAL x86)
    set(TEST_EXE_SOURCES ${TEST_EXE_SOURCES} ${FUNCHOOK_CPU}_test.S)
endif ()


if (NOT MSVC)
    set(FUNCHOOK_ASM_SUFFIX _gas.S)
elseif (FUNCHOOK_CPU MATCHES "^x86")
    enable_language(ASM_MASM)
    set(FUNCHOOK_ASM_SUFFIX _masm.asm)
else ()
    set(FUNCHOOK_CPU noasm)
    set(FUNCHOOK_ASM_SUFFIX .c)
endif ()

add_library(funchook_test SHARED libfunchook_test.c "libfunchook_test_${FUNCHOOK_CPU}${FUNCHOOK_ASM_SUFFIX}")
if (MSVC)
    set_target_properties(funchook_test PROPERTIES OUTPUT_NAME funchook_test_dll)
    if (CMAKE_SIZEOF_VOID_P MATCHES "4")
        set_source_files_properties(libfunchook_test_x86_masm.asm PROPERTIES COMPILE_FLAGS /safeseh)
    endif ()
else ()
    set_target_properties(funchook_test PROPERTIES SUFFIX ".so")
endif ()

set(FUNCHOOK_TEST_LIBS funchook_test)
if (UNIX)
    set(FUNCHOOK_TEST_LIBS ${FUNCHOOK_TEST_LIBS} dl)
endif ()


add_executable(${PROJECT_NAME} ${TEST_EXE_SOURCES})
target_link_libraries(${PROJECT_NAME} PRIVATE funchook::funchook ${FUNCHOOK_TEST_LIBS})
