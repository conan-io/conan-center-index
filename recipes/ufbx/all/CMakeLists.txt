cmake_minimum_required(VERSION 3.10)
project(ufbx C)

option(UFBX_BUILD_SHARED "Build ufbx as a shared library" OFF)
option(UFBX_BUILD_TESTS "Build ufbx tests" OFF)

set(UFBX_SOURCES ufbx.c)
set(UFBX_HEADERS ufbx.h)

# 添加 Windows 导出定义
if(UFBX_BUILD_SHARED AND WIN32)
    add_definitions(-DUFBX_DLL_EXPORT)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

if(UFBX_BUILD_SHARED)
    add_library(ufbx SHARED ${UFBX_SOURCES} ${UFBX_HEADERS})
else()
    add_library(ufbx STATIC ${UFBX_SOURCES} ${UFBX_HEADERS})
endif()

set_target_properties(ufbx PROPERTIES
    PUBLIC_HEADER "${UFBX_HEADERS}"
    OUTPUT_NAME "ufbx"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

if(UFBX_BUILD_TESTS)
    add_executable(ufbx_test test/runner.c)
    target_include_directories(ufbx_test PRIVATE ${CMAKE_CURRENT_SOURCE_DIR} test)
    target_link_libraries(ufbx_test PRIVATE ufbx)
endif()

install(TARGETS ufbx
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
    PUBLIC_HEADER DESTINATION include
)