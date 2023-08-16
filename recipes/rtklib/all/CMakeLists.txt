# Based largely on https://github.com/tomojitakasu/RTKLIB/blob/v2.4.3-b34/app/consapp/rnx2rtkp/gcc/makefile
cmake_minimum_required(VERSION 3.15)
project(rtklib C)

if (NOT MSVC)
    add_compile_options(-Wall -O3 -ansi -pedantic)
    if (GCC)
        add_compile_options(-Wno-unused-but-set-variable)
    endif()
else()
    add_compile_options(/W4 /O2 /D_CRT_SECURE_NO_WARNINGS)
endif()

if (APPLE)
    # Allow extern functions (showmsg(), settspan() and settime()) to be found at runtime
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -undefined dynamic_lookup")
endif()

file(GLOB_RECURSE RTKLIB_SOURCES "src/*.c")

add_library(rtklib ${RTKLIB_SOURCES})
target_include_directories(rtklib PUBLIC src)

include(GNUInstallDirs)
install(TARGETS rtklib)
install(FILES src/rtklib.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
