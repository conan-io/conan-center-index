cmake_minimum_required(VERSION 3.15)
project(jbig LANGUAGES C)

include(GNUInstallDirs)

if(MSVC)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
endif()

add_library(jbig
    ${JBIG_SRC_DIR}/libjbig/jbig.c
    ${JBIG_SRC_DIR}/libjbig/jbig_tab.c
)
target_include_directories(jbig PUBLIC ${JBIG_SRC_DIR}/libjbig)
if(MSVC AND BUILD_SHARED_LIBS)
    target_compile_definitions(jbig PUBLIC _JBIGDLL_)
endif()

install(TARGETS jbig
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES ${JBIG_SRC_DIR}/libjbig/jbig.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

if(BUILD_EXECUTABLES)
    add_executable(pbmtojbg ${JBIG_SRC_DIR}/pbmtools/pbmtojbg.c)
    target_link_libraries(pbmtojbg PRIVATE jbig)

    add_executable(jbgtopbm ${JBIG_SRC_DIR}/pbmtools/jbgtopbm.c)
    target_link_libraries(jbgtopbm PRIVATE jbig)

    install(TARGETS pbmtojbg jbgtopbm DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
