cmake_minimum_required(VERSION 3.4)

project(log.c
	    VERSION 0.1.0
	    LANGUAGES C
	)

# Init Conan stuff
include(conanbuildinfo.cmake)
conan_basic_setup()

# Defines the CMAKE_INSTALL_LIBDIR, CMAKE_INSTALL_BINDIR and many other useful macros.
# See https://cmake.org/cmake/help/latest/module/GNUInstallDirs.html
include(GNUInstallDirs)

set(SRC_FOLDER "source_subfolder")

# To build shared libraries in Windows, we set CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS to TRUE.
# See https://cmake.org/cmake/help/v3.4/variable/CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS.html
# See https://blog.kitware.com/create-dlls-on-windows-without-declspec-using-new-cmake-export-all-feature/
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# Library files SHARED or STATIC set by Conan with BUILD_SHARED_LIBS
add_library(${PROJECT_NAME} ${SRC_FOLDER}/src/log.c ${SRC_FOLDER}/src/log.h)

target_include_directories(${PROJECT_NAME} PUBLIC ${PROJECT_SOURCE_DIR})

# Library info
set_target_properties(${PROJECT_NAME} PROPERTIES
    VERSION ${PROJECT_VERSION}
    C_STANDARD 99)

# Conan options
if (COLOR)
    TARGET_COMPILE_DEFINITIONS(${PROJECT_NAME} PRIVATE LOG_USE_COLOR)
endif()

install(FILES ${SRC_FOLDER}/src/log.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(FILES ${SRC_FOLDER}/LICENSE DESTINATION ${CMAKE_INSTALL_PREFIX}/licenses)
install(TARGETS ${PROJECT_NAME}
LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
