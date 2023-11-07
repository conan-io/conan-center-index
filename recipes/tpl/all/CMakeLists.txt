cmake_minimum_required(VERSION 3.15)
project(tpl LANGUAGES C)

add_library(tpl src/tpl.c)
set_target_properties(tpl PROPERTIES
    VERSION 0.0.0
    SOVERSION 0
)

if(WIN32)
    set_target_properties(tpl PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    target_sources(tpl PRIVATE src/win/mmap.c)
    install(FILES src/win/mman.h DESTINATION include/win)
endif()

install(TARGETS tpl
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
install(FILES src/tpl.h DESTINATION include)
