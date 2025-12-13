cmake_minimum_required(VERSION 3.30) # MASM was fixed in CMake >= 3.30

project(test_package LANGUAGES C ASM_NASM)

if(WIN32)
    set(TEST_ASM_SOURCES hello_windows.asm)
    set(CMAKE_ASM_NASM_OBJECT_FORMAT win64)
elseif(UNIX)
    set(TEST_ASM_SOURCES hello_linux.asm)
    set(CMAKE_ASM_NASM_OBJECT_FORMAT elf64)
else()
    message(FATAL "Not supported operating system")
endif()

set_source_files_properties(${TEST_ASM_SOURCES} PROPERTIES LANGUAGE ASM_NASM)
add_executable(test_package ${TEST_ASM_SOURCES})

if(WIN32)
    target_link_libraries(test_package PRIVATE kernel32.lib)
    target_link_options(test_package PRIVATE /entry:_start /subsystem:console)
endif()
