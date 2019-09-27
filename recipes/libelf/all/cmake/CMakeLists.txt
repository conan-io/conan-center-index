cmake_minimum_required(VERSION 2.8.11)
project(elf C)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

if (EXISTS "${PROJECT_SOURCE_DIR}/lib/sys_elf.h.w32")
    file(RENAME "${PROJECT_SOURCE_DIR}/lib/sys_elf.h.w32" "${PROJECT_SOURCE_DIR}/lib/sys_elf.h")
    file(RENAME "${PROJECT_SOURCE_DIR}/lib/config.h.w32" "${PROJECT_SOURCE_DIR}/config.h")
endif()

file(GLOB_RECURSE SOURCES "${PROJECT_SOURCE_DIR}/lib/*.c")
file(GLOB_RECURSE HEADERS "${PROJECT_SOURCE_DIR}/lib/*.h")

add_library(${PROJECT_NAME} ${SOURCES})
set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${HEADERS}")
target_include_directories(${PROJECT_NAME} SYSTEM PUBLIC "${PROJECT_SOURCE_DIR}/lib")
target_compile_definitions(${PROJECT_NAME} PUBLIC HAVE_MEMCMP=1 HAVE_MEMCPY=1 HAVE_MEMMOVE=1)

if(MSVC AND BUILD_SHARED_LIBS)
    set_target_properties(${PROJECT_NAME} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()

install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
    PUBLIC_HEADER DESTINATION include/libelf
)

install(FILES "${PROJECT_SOURCE_DIR}/lib/libelf.h" DESTINATION include)
install(FILES "${PROJECT_SOURCE_DIR}/lib/gelf.h"   DESTINATION include)
install(FILES "${PROJECT_SOURCE_DIR}/lib/nlist.h"  DESTINATION include)
