cmake_minimum_required (VERSION 3.15)
project (tre)

set(HEADERS
    local_includes/regex.h
    local_includes/tre.h
    win32/tre-config.h
)
file(GLOB SRCS lib/*.c)

include_directories(win32 local_includes)
add_definitions(-D_CRT_SECURE_NO_WARNINGS -D_CRT_NONSTDC_NO_WARNINGS)
add_definitions(-DHAVE_CONFIG_H -DHAVE_MALLOC_H)
add_library(tre ${SRCS} win32/tre.def)

install(TARGETS tre
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(FILES ${HEADERS}
    DESTINATION include/tre
)
