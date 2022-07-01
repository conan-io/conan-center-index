cmake_minimum_required(VERSION 3.1)
project(jbig LANGUAGES C)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

include(GNUInstallDirs)

if(MSVC)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
endif()

add_library(jbig
    source_subfolder/libjbig/jbig.c
    source_subfolder/libjbig/jbig_tab.c
)
target_include_directories(jbig PUBLIC source_subfolder/libjbig)
if(MSVC AND BUILD_SHARED_LIBS)
    target_compile_definitions(jbig PUBLIC _JBIGDLL_)
endif()

install(TARGETS jbig
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES source_subfolder/libjbig/jbig.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

if(BUILD_EXECUTABLES)
    add_executable(pbmtojbg source_subfolder/pbmtools/pbmtojbg.c)
    target_link_libraries(pbmtojbg PRIVATE jbig)

    add_executable(jbgtopbm source_subfolder/pbmtools/jbgtopbm.c)
    target_link_libraries(jbgtopbm PRIVATE jbig)

    install(TARGETS pbmtojbg jbgtopbm DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
