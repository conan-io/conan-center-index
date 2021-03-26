cmake_minimum_required(VERSION 2.8.12)
project(jbig LANGUAGES C)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
endif()

add_library(${CMAKE_PROJECT_NAME} source_subfolder/libjbig/jbig.h
                                  source_subfolder/libjbig/jbig.c
                                  source_subfolder/libjbig/jbig_tab.c)
target_link_libraries(${CMAKE_PROJECT_NAME} ${CONAN_LIBS})
if (WIN32)
    if (BUILD_SHARED_LIBS)
        target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE _JBIGDLL_=1)
    endif()
endif()

include(GNUInstallDirs)

set(OTHER_TARGETS)

if (BUILD_EXECUTABLES)
    add_executable(pbmtojbg source_subfolder/pbmtools/pbmtojbg.c)
    target_link_libraries(pbmtojbg ${CMAKE_PROJECT_NAME})
    target_include_directories(pbmtojbg PRIVATE source_subfolder/libjbig)

    add_executable(jbgtopbm source_subfolder/pbmtools/jbgtopbm.c)
    target_link_libraries(jbgtopbm ${CMAKE_PROJECT_NAME})
    target_include_directories(jbgtopbm PRIVATE source_subfolder/libjbig)

    set(OTHER_TARGETS jbgtopbm pbmtojbg)
endif()

install(TARGETS ${CMAKE_PROJECT_NAME} ${OTHER_TARGETS}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

install(FILES source_subfolder/libjbig/jbig.h DESTINATION include)
