
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

# When using Emscripten, the 'magnum' library provides some additional variables and functions
if(CORRADE_TARGET_EMSCRIPTEN)
    find_file(MAGNUM_EMSCRIPTENAPPLICATION_JS EmscriptenApplication.js
              PATH_SUFFIXES "${CMAKE_CURRENT_LIST_DIR}/../../share/magnum")
    find_file(MAGNUM_WINDOWLESSEMSCRIPTENAPPLICATION_JS WindowlessEmscriptenApplication.js
              PATH_SUFFIXES "${CMAKE_CURRENT_LIST_DIR}/../../share/magnum")
    find_file(MAGNUM_WEBAPPLICATION_CSS WebApplication.css
              PATH_SUFFIXES "${CMAKE_CURRENT_LIST_DIR}/../../share/magnum")

    function(emscripten_embed_file target file destination)
        get_filename_component(absolute_file ${file} ABSOLUTE)
        get_target_property(${target}_LINK_FLAGS ${target} LINK_FLAGS)
        if(NOT ${target}_LINK_FLAGS)
            set(${target}_LINK_FLAGS )
        endif()
        set_target_properties(${target} PROPERTIES LINK_FLAGS "${${target}_LINK_FLAGS} --embed-file ${absolute_file}@${destination}")
    endfunction()
endif()
