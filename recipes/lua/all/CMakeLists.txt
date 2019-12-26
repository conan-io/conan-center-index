cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

if(EXISTS "${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
  include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
else()
  include(conanbuildinfo.cmake)
endif()

conan_basic_setup()

cmake_minimum_required(VERSION 3.1)

project(lua C)

if(NOT SOURCE_SUBDIR)
    message(FATAL_ERROR "Variable 'SOURCE_SUBDIR' must be set to subdirectory where the source resides")
endif()

set(SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE_SUBDIR}")

set(LUA_LIB_SRCS
    ${SOURCE_DIR}/src/lapi.c
    ${SOURCE_DIR}/src/lcode.c
    ${SOURCE_DIR}/src/lctype.c
    ${SOURCE_DIR}/src/ldebug.c
    ${SOURCE_DIR}/src/ldo.c
    ${SOURCE_DIR}/src/ldump.c
    ${SOURCE_DIR}/src/lfunc.c
    ${SOURCE_DIR}/src/lgc.c
    ${SOURCE_DIR}/src/llex.c
    ${SOURCE_DIR}/src/lmem.c
    ${SOURCE_DIR}/src/lobject.c
    ${SOURCE_DIR}/src/lopcodes.c
    ${SOURCE_DIR}/src/lparser.c
    ${SOURCE_DIR}/src/lstate.c
    ${SOURCE_DIR}/src/lstring.c
    ${SOURCE_DIR}/src/ltable.c
    ${SOURCE_DIR}/src/ltm.c
    ${SOURCE_DIR}/src/lundump.c
    ${SOURCE_DIR}/src/lvm.c
    ${SOURCE_DIR}/src/lzio.c
    ${SOURCE_DIR}/src/lauxlib.c
    ${SOURCE_DIR}/src/lbaselib.c
    ${SOURCE_DIR}/src/lbitlib.c
    ${SOURCE_DIR}/src/lcorolib.c
    ${SOURCE_DIR}/src/ldblib.c
    ${SOURCE_DIR}/src/liolib.c
    ${SOURCE_DIR}/src/lmathlib.c
    ${SOURCE_DIR}/src/loslib.c
    ${SOURCE_DIR}/src/lstrlib.c
    ${SOURCE_DIR}/src/ltablib.c
    ${SOURCE_DIR}/src/lutf8lib.c
    ${SOURCE_DIR}/src/loadlib.c
    ${SOURCE_DIR}/src/linit.c
    ${SOURCE_DIR}/src/luac.c
)

add_library(${PROJECT_NAME} ${LUA_LIB_SRCS})
set(INCLUDE_DIR "${SOURCE_DIR}/src")
target_include_directories(${PROJECT_NAME}
    PRIVATE ${INCLUDE_DIR}
)
if(WIN32)
        target_compile_definitions(${PROJECT_NAME} PRIVATE -D_CRT_SECURE_NO_WARNINGS)
endif()


IF (UNIX)
    IF (APPLE)
        TARGET_COMPILE_DEFINITIONS (lua PUBLIC -DLUA_USE_DLOPEN)
    ELSE ()
        FIND_LIBRARY (LIB_DLOPEN NAMES dl)
        IF (LIB_DLOPEN)
            TARGET_COMPILE_DEFINITIONS (lua PUBLIC -DLUA_USE_DLOPEN)
            TARGET_LINK_LIBRARIES (lua ${LIB_DLOPEN})
        ENDIF ()
    ENDIF ()
ENDIF ()



# Must use GNUInstallDirs to install libraries into correct
# locations on all platforms.
include(GNUInstallDirs)

set(INSTALL_DIR "${CMAKE_BINARY_DIR}/install")
install(
	TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} # This is for Windows
)
install(
	FILES
        "${INCLUDE_DIR}/lua.h"
        "${INCLUDE_DIR}/lua.hpp"
        "${INCLUDE_DIR}/lualib.h"
        "${INCLUDE_DIR}/lauxlib.h"
        "${INCLUDE_DIR}/luaconf.h"
	DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_NAME}
)
