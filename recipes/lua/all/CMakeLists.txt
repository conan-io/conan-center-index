cmake_minimum_required(VERSION 2.8.12)
project(lua)

include(conanbuildinfo.cmake)
conan_basic_setup()



# The following was originally taken from: https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/lua/CMakeLists.txt

# Lua can be compiled as either C or C++.
# Default configuration is C, set COMPILE_AS_CPP to ON to use C++.
# See http://stackoverflow.com/questions/13560945/c-and-c-library-using-longjmp for why would you want to do that.
# Primary differences:
# - Exceptions will be used instead of setjmp/longjmp
# - The name mangling for functions will be C++ instead of C.
#     - This is a source-incompatible change because extern "C" is chosen by the including application.
# - The lua.hpp header will not be available.

SET(SOURCE_DIR ${CMAKE_SOURCE_DIR}/${SOURCE_SUBDIR} )

# Build Libraries
SET (SRC_LIBLUA
${SOURCE_DIR}/src/lapi.c ${SOURCE_DIR}/src/lauxlib.c ${SOURCE_DIR}/src/lbaselib.c ${SOURCE_DIR}/src/lcode.c ${SOURCE_DIR}/src/lcorolib.c
${SOURCE_DIR}/src/lctype.c ${SOURCE_DIR}/src/ldblib.c ${SOURCE_DIR}/src/ldebug.c ${SOURCE_DIR}/src/ldo.c ${SOURCE_DIR}/src/ldump.c ${SOURCE_DIR}/src/lfunc.c ${SOURCE_DIR}/src/lgc.c
${SOURCE_DIR}/src/linit.c ${SOURCE_DIR}/src/liolib.c ${SOURCE_DIR}/src/llex.c ${SOURCE_DIR}/src/lmathlib.c ${SOURCE_DIR}/src/lmem.c ${SOURCE_DIR}/src/loadlib.c ${SOURCE_DIR}/src/lobject.c
${SOURCE_DIR}/src/lopcodes.c ${SOURCE_DIR}/src/loslib.c ${SOURCE_DIR}/src/lparser.c ${SOURCE_DIR}/src/lstate.c ${SOURCE_DIR}/src/lstring.c ${SOURCE_DIR}/src/lstrlib.c
${SOURCE_DIR}/src/ltable.c ${SOURCE_DIR}/src/ltablib.c ${SOURCE_DIR}/src/ltm.c ${SOURCE_DIR}/src/lundump.c ${SOURCE_DIR}/src/lutf8lib.c ${SOURCE_DIR}/src/lvm.c ${SOURCE_DIR}/src/lzio.c
)

IF(LUA_VERSION VERSION_LESS 5.4.0)
    LIST(APPEND SRC_LIBLUA ${SOURCE_DIR}/src/lbitlib.c)
ENDIF()

IF (COMPILE_AS_CPP)
    SET_SOURCE_FILES_PROPERTIES(${SRC_LIBLUA} ${SOURCE_DIR}/src/lua.c ${SOURCE_DIR}/src/luac.c PROPERTIES LANGUAGE CXX)
ELSE ()
    SET (CMAKE_C_STANDARD 99)
ENDIF ()

IF (WIN32)
    # remove warnings
    ADD_DEFINITIONS (-D_CRT_SECURE_NO_WARNINGS )
ENDIF ()

IF (UNIX)
    IF (NOT ANDROID)
        ADD_DEFINITIONS (-DLUA_USE_POSIX)
    ENDIF ()
    FIND_LIBRARY (LIB_MATH NAMES m)
    IF (LIB_MATH)
        LINK_LIBRARIES (${LIB_MATH})
    ENDIF ()
ENDIF ()

#DLL
ADD_LIBRARY ( lua ${SRC_LIBLUA} )
IF (COMPILE_AS_CPP)
    SET_TARGET_PROPERTIES(lua PROPERTIES OUTPUT_NAME "lua-c++")
ENDIF()

IF (BUILD_SHARED_LIBS AND WIN32)
    TARGET_COMPILE_DEFINITIONS (lua PUBLIC -DLUA_BUILD_AS_DLL )
ENDIF ()

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

INSTALL ( TARGETS lua
    RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}/bin
    LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/lib
    ARCHIVE DESTINATION ${CMAKE_INSTALL_PREFIX}/lib
)

IF (NOT DEFINED SKIP_INSTALL_TOOLS)
    ADD_EXECUTABLE ( luac ${SOURCE_DIR}/src/luac.c ${SRC_LIBLUA} ) # compiler uses non-exported APIs, so must include sources directly.
    ADD_EXECUTABLE ( luai ${SOURCE_DIR}/src/lua.c )  # interpreter
    TARGET_LINK_LIBRARIES ( luai lua )
    SET_TARGET_PROPERTIES ( luai PROPERTIES OUTPUT_NAME lua PDB_NAME luai )
    IF (UNIX)
        IF (CMAKE_SYSTEM_NAME STREQUAL FreeBSD)
            SET (_LIB_READLINE_NAME edit)
        ELSE ()
            SET (_LIB_READLINE_NAME readline)
        ENDIF ()
        FIND_LIBRARY (LIB_READLINE NAMES ${_LIB_READLINE_NAME})
        IF (LIB_READLINE)
            TARGET_COMPILE_DEFINITIONS (luai PUBLIC -DLUA_USE_READLINE)
            TARGET_LINK_LIBRARIES(luai ${LIB_READLINE})
            IF (_LIB_READLINE_NAME STREQUAL edit)
                TARGET_INCLUDE_DIRECTORIES (luai PUBLIC /usr/include/edit)
            ENDIF ()
        ENDIF ()
    ENDIF ()
    INSTALL ( TARGETS luai luac RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}/tools/lua )
ENDIF ()

IF (NOT DEFINED SKIP_INSTALL_HEADERS)
    INSTALL(
        FILES
            ${SOURCE_DIR}/src/lualib.h
            ${SOURCE_DIR}/src/lua.h
            ${SOURCE_DIR}/src/luaconf.h
            ${SOURCE_DIR}/src/lauxlib.h
        DESTINATION include
    )
    # If using C++, don't install extern "C" wrapper.
    IF (NOT COMPILE_AS_CPP)
        INSTALL(FILES ${SOURCE_DIR}/src/lua.hpp DESTINATION include)
    ENDIF ()
ENDIF ()
