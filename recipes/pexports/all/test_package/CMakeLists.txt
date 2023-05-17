cmake_minimum_required(VERSION 3.1)
project(test_package C)

if(NOT WIN32)
    message(FATAL_ERROR "pexports only supports Windows")
endif()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_program(PEXPORTS_BIN "pexports")
set(EXPORTS_DEF_PATH "${CMAKE_BINARY_DIR}/exports.def")
if(MSVC)
    set(IMPORT_LIB "${CMAKE_BINARY_DIR}/my_import.lib")
    set(LIB_BIN ${CMAKE_AR})
    if(NOT LIB_BIN)
        set(LIB_BIN lib)
    endif()
    separate_arguments(IMPORT_LIB_ARGS WINDOWS_COMMAND ${CMAKE_EXE_LINKER_FLAGS})
    set(CREATE_IMPORT_LIB_CMD ${LIB_BIN} -def:${EXPORTS_DEF_PATH} -out:${IMPORT_LIB} ${IMPORT_LIB_ARGS})
elseif(MINGW)
    set(IMPORT_LIB "${CMAKE_BINARY_DIR}/libmy_import.a")
    set(LIB_BIN ${CMAKE_DLLTOOL})
    if(NOT LIB_BIN)
        set(LIB_BIN dlltool)
    endif()
    set(CREATE_IMPORT_LIB_CMD ${LIB_BIN} -d ${EXPORTS_DEF_PATH} -l ${IMPORT_LIB})
else()
    message(FATAL_ERROR "Unknown toolchain targeting Windows. Don't know how to create an import library.")
endif()

add_custom_command(OUTPUT "${CMAKE_BINARY_DIR}/dllname.txt"
    COMMAND "${CMAKE_COMMAND}" -E echo "$<TARGET_FILE:test_library>" >"${CMAKE_BINARY_DIR}/dllname.txt"
    COMMENT "[debug] Write path of dll to ${CMAKE_BINARY_DIR}/dllname.txt (for debug purposes)"
    DEPENDS test_library
)

add_custom_command(OUTPUT "${EXPORTS_DEF_PATH}"
    COMMAND "${PEXPORTS_BIN}" "$<TARGET_FILE:test_library>">${EXPORTS_DEF_PATH}
    COMMENT "[pexports] Create ${EXPORTS_DEF_PATH}"
    DEPENDS test_library
)

add_custom_command(OUTPUT "${IMPORT_LIB}"
    COMMAND ${CREATE_IMPORT_LIB_CMD}
    COMMENT "[import] Create import library ${IMPORT_LIB}"
    DEPENDS "${EXPORTS_DEF_PATH}"
)

add_custom_target(create_import_library ALL DEPENDS "${CMAKE_BINARY_DIR}/dllname.txt" "${IMPORT_LIB}")

add_library(test_library SHARED test_library.c)

add_executable(${PROJECT_NAME} test_package)
target_link_libraries(${PROJECT_NAME} PRIVATE my_import)
target_link_directories(${PROJECT_NAME} PRIVATE "${CMAKE_BINARY_DIR}")
add_dependencies(${PROJECT_NAME} create_import_library)
