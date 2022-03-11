cmake_minimum_required(VERSION 2.8.12)
project(jbig LANGUAGES C)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
endif()

add_library(${PROJECT_NAME} source_subfolder/libjbig/jbig.c
                            source_subfolder/libjbig/jbig_tab.c)
if(MSVC AND BUILD_SHARED_LIBS)
    target_compile_definitions(${PROJECT_NAME} PUBLIC _JBIGDLL_)
endif()

install(TARGETS ${PROJECT_NAME}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES source_subfolder/libjbig/jbig.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

if (BUILD_EXECUTABLES)
    add_executable(pbmtojbg source_subfolder/pbmtools/pbmtojbg.c)
    target_link_libraries(pbmtojbg ${PROJECT_NAME})
    target_include_directories(pbmtojbg PRIVATE source_subfolder/libjbig)

    add_executable(jbgtopbm source_subfolder/pbmtools/jbgtopbm.c)
    target_link_libraries(jbgtopbm ${PROJECT_NAME})
    target_include_directories(jbgtopbm PRIVATE source_subfolder/libjbig)

    install(TARGETS pbmtojbg jbgtopbm DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
