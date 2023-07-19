cmake_minimum_required(VERSION 3.15)
project(WinEditLine C)

add_library(edit
    src/editline.c
    src/fn_complete.c
    src/history.c
    src/libedit.def
)
target_include_directories(edit PRIVATE src)

install(TARGETS edit
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
install(DIRECTORY src/editline DESTINATION include)
