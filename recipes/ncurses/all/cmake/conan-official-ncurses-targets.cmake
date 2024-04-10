# Reproduces the variables set by https://cmake.org/cmake/help/latest/module/FindCurses.html
set(CURSES_FOUND ON)
set(CURSES_INCLUDE_DIRS ${Curses_INCLUDE_DIRS})
set(CURSES_CFLAGS ${Curses_DEFINITIONS} ${Curses_COMPILE_OPTIONS_C})
set(CURSES_HAVE_CURSES_H OFF)
set(CURSES_HAVE_NCURSES_H OFF)
if(CURSES_NEED_NCURSES)
    set(CURSES_HAVE_NCURSES_CURSES_H ON)
    set(CURSES_HAVE_NCURSES_NCURSES_H ON)
endif()

# For backward compatibility with Conan v1
string(TOUPPER "${CMAKE_BUILD_TYPE}" _CONFIG)
set(CURSES_INCLUDE_DIRS ${CURSES_INCLUDE_DIRS}
    ${ncurses_INCLUDE_DIRS_${_CONFIG}}
    ${Curses_INCLUDE_DIRS_${_CONFIG}}
)
set(CURSES_CFLAGS ${CURSES_CFLAGS}
    ${ncurses_DEFINITIONS_${_CONFIG}} ${ncurses_COMPILE_OPTIONS_C_${_CONFIG}}
    ${Curses_DEFINITIONS_${_CONFIG}} ${Curses_COMPILE_OPTIONS_C_${_CONFIG}}
)

# CURSES_LIBRARIES output from CMake uses absolute paths for the libraries
list (GET CURSES_INCLUDE_DIRS 0 _first_include_dir)
get_filename_component(CURSES_LIB_DIRS  "${_first_include_dir}/../lib" ABSOLUTE)
foreach(_LIB ${Curses_LIBRARIES} ${ncurses_LIBRARIES_${_CONFIG}} ${Curses_LIBRARIES_${_CONFIG}})
    if(TARGET ${_LIB} OR IS_ABSOLUTE ${_LIB})
        list(APPEND CURSES_LIBRARIES ${_LIB})
    else()
        find_library(_LIB ${_LIB} PATHS ${CURSES_LIB_DIRS})
        list(APPEND CURSES_LIBRARIES ${_LIB})
    endif()
endforeach()

set(CURSES_INCLUDE_DIR ${CURSES_INCLUDE_DIRS})
set(CURSES_LIBRARY ${CURSES_LIBRARIES})
