cmake_minimum_required(VERSION 3.0)
project(test_package)

set(CURSES_NEED_NCURSES TRUE)
find_package(Curses REQUIRED)

if(NOT CURSES_HAVE_NCURSES_NCURSES_H)
    message(FATAL_ERROR "ncurses/ncurses.h is not available (CURSES_HAVE_NCURSES_NCURSES_H)")
endif()

if(NOT CURSES_HAVE_NCURSES_CURSES_H)
    message(FATAL_ERROR "ncurses/curses.h is not available (CURSES_HAVE_NCURSES_CURSES_H)")
endif()

add_executable(${PROJECT_NAME} test_package.c)
target_compile_definitions(${PROJECT_NAME} PRIVATE ${CURSES_CFLAGS})
target_include_directories(${PROJECT_NAME} PRIVATE ${CURSES_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME} PRIVATE ${CURSES_LIBRARIES})
