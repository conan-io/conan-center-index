cmake_minimum_required(VERSION 3.4)
project(jbig LANGUAGES C)

include(conanbuildinfo.cmake)
conan_basic_setup()

if (WIN32 AND MSVC AND BUILD_SHARED_LIBS)
    set(WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

add_library(${CMAKE_PROJECT_NAME} source_subfolder/libjbig/jbig.h
                                  source_subfolder/libjbig/jbig.c
                                  source_subfolder/libjbig/jbig_tab.c)
target_link_libraries(${CMAKE_PROJECT_NAME} ${CONAN_LIBS})

include(GNUInstallDirs)

install(TARGETS ${CMAKE_PROJECT_NAME}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

install(FILES source_subfolder/libjbig/jbig.h DESTINATION include)
