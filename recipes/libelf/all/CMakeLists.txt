cmake_minimum_required(VERSION 3.4)
project(elf C)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(EXISTS "${PROJECT_SOURCE_DIR}/source_subfolder/lib/sys_elf.h.w32")
    file(RENAME "${PROJECT_SOURCE_DIR}/source_subfolder/lib/sys_elf.h.w32" "${PROJECT_SOURCE_DIR}/source_subfolder/lib/sys_elf.h")
    file(RENAME "${PROJECT_SOURCE_DIR}/source_subfolder/lib/config.h.w32" "${PROJECT_SOURCE_DIR}/source_subfolder/config.h")
endif()

file(GLOB_RECURSE SOURCES "source_subfolder/lib/*.c")
file(GLOB_RECURSE HEADERS "source_subfolder/lib/*.h")

add_library(${PROJECT_NAME} ${SOURCES})
set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${HEADERS}")
target_include_directories(${PROJECT_NAME} SYSTEM PUBLIC "source_subfolder/lib")
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

install(FILES "source_subfolder/lib/libelf.h" DESTINATION include)
install(FILES "source_subfolder/lib/gelf.h"   DESTINATION include)
install(FILES "source_subfolder/lib/nlist.h"  DESTINATION include)
