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
    set(CREATE_IMPORT_LIB_CMD ${CMAKE_AR} -def:${EXPORTS_DEF_PATH} -out:my_import.lib ${CMAKE_EXE_LINKER_FLAGS})
elseif(MINGW)
    set(CREATE_IMPORT_LIB_CMD ${CMAKE_DLLTOOL} -d ${EXPORTS_DEF_PATH} -l libmy_import.a)
else()
    message(FATAL_ERROR "Unknown toolchain targeting Windows. Don't know how to create an import library.")
endif()

add_library(test_library SHARED test_library.c)
add_custom_command(TARGET test_library POST_BUILD
    COMMAND "${CMAKE_COMMAND}" -E echo "$<TARGET_FILE:test_library>" >"${CMAKE_BINARY_DIR}/dllname.txt"
    COMMAND "${PEXPORTS_BIN}" "$<TARGET_FILE:test_library>">${EXPORTS_DEF_PATH}
    COMMAND ${CREATE_IMPORT_LIB_CMD}
)

add_executable(${PROJECT_NAME} test_package)
target_link_libraries(${PROJECT_NAME} PRIVATE my_import)
target_link_directories(${PROJECT_NAME} PRIVATE "${CMAKE_BINARY_DIR}")
add_dependencies(${PROJECT_NAME} test_library)
