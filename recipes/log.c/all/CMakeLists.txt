cmake_minimum_required(VERSION 3.16)

project(log.c
	    VERSION 0.1.0
	    DESCRIPTION "A simple logging library implemented in C99"
	    HOMEPAGE_URL "https://github.com/rxi/log.c"
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
add_library(${PROJECT_NAME} ${SRC_FOLDER}/src/log.c ${SRC_FOLDER}/src/log.h "${PROJECT_BINARY_DIR}/log_export.h")


include(GenerateExportHeader)
generate_export_header(${PROJECT_NAME} BASE_NAME log)

target_include_directories(${PROJECT_NAME} PUBLIC ${PROJECT_SOURCE_DIR} ${PROJECT_BINARY_DIR})

# Library info
set_target_properties(${PROJECT_NAME} PROPERTIES
    VERSION ${PROJECT_VERSION}
	C_STANDARD 99)

# Conan options
if (COLOR)
    TARGET_COMPILE_DEFINITIONS(${PROJECT_NAME} PRIVATE LOG_USE_COLOR)
    message(STATUS "LOG_USE_COLOR")
endif()

install(FILES ${SRC_FOLDER}/src/log.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(FILES ${PROJECT_BINARY_DIR}/log_export.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(FILES ${SRC_FOLDER}/LICENSE DESTINATION ${CMAKE_INSTALL_PREFIX}/licenses)
install(TARGETS ${PROJECT_NAME}
LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
RUNTIME DESTINATION bin)

message(STATUS "summary of build options:
    Install prefix:  ${CMAKE_INSTALL_PREFIX}
    Target system:   ${CMAKE_SYSTEM_NAME}
	Build shared lib:    ${BUILD_SHARED_LIBS}
    Compiler:
      C compiler:    ${CMAKE_C_COMPILER}
      CFLAGS:        ${CMAKE_C_FLAGS_${_build_type}} ${CMAKE_C_FLAGS}
")

