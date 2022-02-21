
# Here we are reproducing the variables and call performed by the FindCorrade.cmake provided by the library

# Read flags from configuration
file(READ "${CMAKE_CURRENT_LIST_DIR}/../../include/Corrade/configure.h" _corradeConfigure)
string(REGEX REPLACE ";" "\\\\;" _corradeConfigure "${_corradeConfigure}")
string(REGEX REPLACE "\n" ";" _corradeConfigure "${_corradeConfigure}")
set(_corradeFlags
    MSVC2015_COMPATIBILITY
    MSVC2017_COMPATIBILITY
    MSVC2019_COMPATIBILITY
    BUILD_DEPRECATED
    BUILD_STATIC
    BUILD_STATIC_UNIQUE_GLOBALS
    BUILD_MULTITHREADED
    TARGET_UNIX
    TARGET_APPLE
    TARGET_IOS
    TARGET_IOS_SIMULATOR
    TARGET_WINDOWS
    TARGET_WINDOWS_RT
    TARGET_EMSCRIPTEN
    TARGET_ANDROID
    # TARGET_X86 etc and TARGET_LIBCXX are not exposed to CMake as the meaning
    # is unclear on platforms with multi-arch binaries or when mixing different
    # STL implementations. TARGET_GCC etc are figured out via UseCorrade.cmake,
    # as the compiler can be different when compiling the lib & when using it.
    PLUGINMANAGER_NO_DYNAMIC_PLUGIN_SUPPORT
    TESTSUITE_TARGET_XCTEST
    UTILITY_USE_ANSI_COLORS)
foreach(_corradeFlag ${_corradeFlags})
    list(FIND _corradeConfigure "#define CORRADE_${_corradeFlag}" _corrade_${_corradeFlag})
    if(NOT _corrade_${_corradeFlag} EQUAL -1)
        set(CORRADE_${_corradeFlag} 1)
    endif()
endforeach()


# Corrade::rc, a target with just an executable
if(NOT TARGET Corrade::rc)
    if(CMAKE_CROSSCOMPILING)
        find_program(CORRADE_RC_PROGRAM 
            NAMES corrade-rc 
            PATHS ENV 
            PATH NO_DEFAULT_PATH)
    else()
        find_program(CORRADE_RC_PROGRAM 
            NAMES corrade-rc 
            PATHS "${CMAKE_CURRENT_LIST_DIR}/../../bin/"
            NO_DEFAULT_PATH)
    endif()

    get_filename_component(CORRADE_RC_PROGRAM "${CORRADE_RC_PROGRAM}" ABSOLUTE)

    add_executable(Corrade::rc IMPORTED)
    set_property(TARGET Corrade::rc PROPERTY IMPORTED_LOCATION ${CORRADE_RC_PROGRAM})
endif()

# Include and declare other build modules
include("${CMAKE_CURRENT_LIST_DIR}/UseCorrade.cmake")
set(CORRADE_LIB_SUFFIX_MODULE "${CMAKE_CURRENT_LIST_DIR}/CorradeLibSuffix.cmake")
