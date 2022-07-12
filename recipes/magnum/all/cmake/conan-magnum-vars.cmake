
# Here we are reproducing the variables and call performed by the FindMagnum.cmake provided by the library

# Read flags from configuration
file(READ "${CMAKE_CURRENT_LIST_DIR}/../../include/Magnum/configure.h" _magnumConfigure)
string(REGEX REPLACE ";" "\\\\;" _magnumConfigure "${_magnumConfigure}")
string(REGEX REPLACE "\n" ";" _magnumConfigure "${_magnumConfigure}")
set(_magnumFlags
    BUILD_DEPRECATED
    BUILD_STATIC
    BUILD_STATIC_UNIQUE_GLOBALS
    TARGET_GL
    TARGET_GLES
    TARGET_GLES2
    TARGET_GLES3
    TARGET_DESKTOP_GLES
    TARGET_WEBGL
    TARGET_HEADLESS
    TARGET_VK)
foreach(_magnumFlag ${_magnumFlags})
    list(FIND _magnumConfigure "#define MAGNUM_${_magnumFlag}" _magnum_${_magnumFlag})
    if(NOT _magnum_${_magnumFlag} EQUAL -1)
        set(MAGNUM_${_magnumFlag} 1)
    endif()
endforeach()
