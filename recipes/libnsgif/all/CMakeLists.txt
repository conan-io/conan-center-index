cmake_minimum_required(VERSION 3.15)
project(libnsgif C)

add_library(libnsgif 
        src/utils/log.h
        src/libnsgif.c
        src/libnsgif.h
        src/lzw.c
        src/lzw.h
)

set_target_properties(libnsgif PROPERTIES PUBLIC_HEADER "src/libnsgif.h")
install(TARGETS libnsgif DESTINATION "."
        PUBLIC_HEADER DESTINATION include
        RUNTIME DESTINATION bin
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        )
