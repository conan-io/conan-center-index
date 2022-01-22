cmake_minimum_required(VERSION 3.4)
project(miniaudio C)

include(GNUInstallDirs)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(SOURCE_SUBFOLDER ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/extras)
add_library(miniaudio ${SOURCE_SUBFOLDER}/miniaudio_split/miniaudio.c)
target_include_directories(miniaudio PRIVATE ${SOURCE_SUBFOLDER}/miniaudio_split/)

if (BUILD_SHARED_LIBS)
    target_compile_definitions(miniaudio PRIVATE MA_DLL MINIAUDIO_IMPLEMENTATION)
endif()

set_target_properties(miniaudio PROPERTIES VERSION ${MINIAUDIO_VERSION_STRING})

install(TARGETS miniaudio
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
