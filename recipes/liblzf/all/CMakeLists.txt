cmake_minimum_required(VERSION 3.15)
project(liblzf LANGUAGES C)

add_library(liblzf
    src/lzf_c.c
    src/lzf_d.c
)
set_target_properties(liblzf PROPERTIES OUTPUT_NAME lzf)

# The original autotools config specified -O3 -funroll-all-loops for GCC
if(CMAKE_C_COMPILER_ID STREQUAL "GNU" OR
   CMAKE_C_COMPILER_ID STREQUAL "Clang")
    target_compile_options(liblzf PRIVATE "$<$<CONFIG:Release>:-O3>")
    target_compile_options(liblzf PRIVATE "$<$<CONFIG:RelWithDebInfo>:-O3>")
elseif(CMAKE_C_COMPILER_ID STREQUAL "MSVC")
    target_compile_options(liblzf PRIVATE "$<$<CONFIG:Release>:/O2>")
    target_compile_options(liblzf PRIVATE "$<$<CONFIG:RelWithDebInfo>:/O2>")
endif()
if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    target_compile_options(liblzf PRIVATE "-funroll-all-loops")
endif()

set_target_properties(liblzf PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    PUBLIC_HEADER src/lzf.h
)

install(TARGETS liblzf
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
