cmake_minimum_required(VERSION 3.4)
project(miniaudio LANGUAGES C)

include(GNUInstallDirs)

set(SOURCE_SUBFOLDER ${MINIAUDIO_SRC_DIR}/extras/miniaudio_split/)
add_library(miniaudio ${SOURCE_SUBFOLDER}/miniaudio.c)
target_include_directories(miniaudio PRIVATE ${SOURCE_SUBFOLDER})

if (BUILD_SHARED_LIBS)
    target_compile_definitions(miniaudio PRIVATE MA_DLL MINIAUDIO_IMPLEMENTATION)
endif()

set_target_properties(miniaudio
        PROPERTIES
        VERSION ${MINIAUDIO_VERSION_STRING}
        PUBLIC_HEADER ${SOURCE_SUBFOLDER}/miniaudio.h)

install(TARGETS miniaudio
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
