cmake_minimum_required(VERSION 2.6)
cmake_policy(SET CMP0005 NEW) # do not escape preprocessor defines

project(libflac)

include(CheckFunctionExists)
include(CheckIncludeFiles)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(FLAC_SRC_DIR ${PROJECT_SOURCE_DIR}/source_subfolder)

file(GLOB LIBFLAC_SOURCES ${FLAC_SRC_DIR}/src/libFLAC/*.c)

if(WIN32)
  list(APPEND LIBFLAC_SOURCES 
    ${FLAC_SRC_DIR}/src/share/win_utf8_io/win_utf8_io.c)
else()
  list(REMOVE_ITEM LIBFLAC_SOURCES
    ${FLAC_SRC_DIR}/src/libFLAC/windows_unicode_filenames.c)
endif()

file(GLOB LIBFLACXX_SOURCES
    ${FLAC_SRC_DIR}/src/libFLAC++/*.cpp)

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()

add_library(libFLAC ${LIBFLAC_SOURCES})
add_library(libFLACXX ${LIBFLACXX_SOURCES})

target_include_directories(libFLAC   PUBLIC  ${FLAC_SRC_DIR}/include)
target_include_directories(libFLACXX PUBLIC  ${FLAC_SRC_DIR}/include)
target_include_directories(libFLAC   PRIVATE ${FLAC_SRC_DIR}/src/libFLAC/include)
target_include_directories(libFLACXX PRIVATE ${FLAC_SRC_DIR}/src/libFLAC/include)

if(NOT ${CONAN_SETTINGS_ARCH} MATCHES arm)
    target_compile_definitions(libFLAC 
        PRIVATE -DFLAC__SSE_OS -DFLAC__HAS_X86INTRIN)
    target_compile_definitions(libFLACXX 
        PRIVATE -DFLAC__SSE_OS -DFLAC__HAS_X86INTRIN)
endif()

if(${CONAN_SETTINGS_ARCH} STREQUAL "x86")
    target_compile_definitions(libFLAC 
        PRIVATE -DFLAC__CPU_IA32)
    target_compile_definitions(libFLACXX 
        PRIVATE -DFLAC__CPU_IA32)
    if(USE_ASM)
        target_compile_definitions(libFLAC   PRIVATE -DFLAC__HAS_NASM)
        target_compile_definitions(libFLACXX PRIVATE -DFLAC__HAS_NASM)
        file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/nasm)
        foreach(ASM_SOURCE cpu_asm fixed_asm lpc_asm)
            execute_process(COMMAND nasm "-i${FLAC_SRC_DIR}/src/libFLAC/ia32/" -f win32 -d OBJ_FORMAT_win32 -f win32 
                -o "${CMAKE_BINARY_DIR}/nasm/${ASM_SOURCE}.obj" "${FLAC_SRC_DIR}/src/libFLAC/ia32/${ASM_SOURCE}.nasm"
                WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
            list(APPEND LIBFLAC_SOURCES ${CMAKE_BINARY_DIR}/nasm/${ASM_SOURCE}.obj)
        endforeach()
    endif()
elseif(${CONAN_SETTINGS_ARCH} STREQUAL "x86_64")
    target_compile_definitions(libFLAC 
        PRIVATE -DFLAC__CPU_X86_64 -DENABLE_64_BIT_WORDS)
    target_compile_definitions(libFLACXX 
        PRIVATE -DFLAC__CPU_X86_64 -DENABLE_64_BIT_WORDS)
endif()

if(NOT USE_ASM)
    target_compile_definitions(libFLAC   PRIVATE -DFLAC__NO_ASM)
    target_compile_definitions(libFLACXX PRIVATE -DFLAC__NO_ASM)
endif()

check_include_files(sys/param.h HAVE_SYSPARAM_H)
check_include_files(stdint.h HAVE_STDINT_H)
check_include_files(inttypes.h HAVE_INTTYPES_H)

if(UNIX)
  set(CMAKE_REQUIRED_LIBRARIES m)
endif()
check_function_exists(lround HAVE_LROUND)
check_function_exists(fseeko HAVE_FSEEKO)

if(HAVE_LROUND)
  target_compile_definitions(libFLAC   PUBLIC -DHAVE_LROUND)
  target_compile_definitions(libFLACXX PUBLIC -DHAVE_LROUND)
endif()
if(HAVE_FSEEKO)
  target_compile_definitions(libFLAC   PUBLIC -DHAVE_FSEEKO)
  target_compile_definitions(libFLACXX PUBLIC -DHAVE_FSEEKO)
endif()
if(HAVE_SYSPARAM_H)
  target_compile_definitions(libFLAC   PUBLIC -DHAVE_SYS_PARAM_H)
  target_compile_definitions(libFLACXX PUBLIC -DHAVE_SYS_PARAM_H)
endif()
if(HAVE_STDINT_H)
  target_compile_definitions(libFLAC   PUBLIC -DHAVE_STDINT_H)
  target_compile_definitions(libFLACXX PUBLIC -DHAVE_STDINT_H)
endif()
if(HAVE_INTTYPES_H)
  target_compile_definitions(libFLAC   PUBLIC -DHAVE_INTTYPES_H)
  target_compile_definitions(libFLACXX PUBLIC -DHAVE_INTTYPES_H)
endif()

if(CMAKE_BUILD_TYPE MATCHES Debug)
  target_compile_definitions(libFLAC   PUBLIC -DFLAC__OVERFLOW_DETECT)
  target_compile_definitions(libFLACXX PUBLIC -DFLAC__OVERFLOW_DETECT)
endif()

target_compile_definitions(libFLAC   
  PUBLIC -DFLAC__HAS_OGG -DFLAC__ALIGN_MALLOC_DATA 
         -D_CRT_SECURE_NO_WARNINGS -D_CRT_NONSTDC_NO_WARNINGS
         -DPACKAGE_VERSION="1.3.2")
target_compile_definitions(libFLACXX 
  PUBLIC -DFLAC__HAS_OGG -DFLAC__ALIGN_MALLOC_DATA 
         -D_CRT_SECURE_NO_WARNINGS -D_CRT_NONSTDC_NO_WARNINGS
         -DPACKAGE_VERSION="1.3.2")

set_target_properties(libFLAC PROPERTIES OUTPUT_NAME flac)
set_target_properties(libFLACXX PROPERTIES OUTPUT_NAME flac++)

if(BUILD_SHARED_LIBS)
  set_target_properties(libFLACXX PROPERTIES COMPILE_FLAGS -DFLACPP_API_EXPORTS)
  set_target_properties(libFLAC PROPERTIES COMPILE_FLAGS -DFLAC_API_EXPORTS)
else()
  target_compile_definitions(libFLACXX PUBLIC -DFLAC__NO_DLL)
  target_compile_definitions(libFLAC   PUBLIC -DFLAC__NO_DLL)
endif()

install(TARGETS libFLAC libFLACXX
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib)

target_link_libraries(libFLAC ${CONAN_LIBS})
target_link_libraries(libFLACXX libFLAC)

if(NOT DEFINED LIBFLAC_SKIP_HEADERS)
    install(DIRECTORY ${FLAC_SRC_DIR}/include/FLAC/
        DESTINATION include/FLAC
        FILES_MATCHING PATTERN "*.h")
    install(DIRECTORY ${FLAC_SRC_DIR}/include/FLAC++/
        DESTINATION include/FLAC++
        FILES_MATCHING PATTERN "*.h")
    install(DIRECTORY ${FLAC_SRC_DIR}/include/share/
        DESTINATION include/share
        FILES_MATCHING PATTERN "*.h")
endif()