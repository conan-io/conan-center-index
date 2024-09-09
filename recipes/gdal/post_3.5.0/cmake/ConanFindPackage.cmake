function(define_find_package2 pkgname include_file library_name)
endfunction()
function(find_package2 pkgname)
    # Remove args unsupported by find_package()
    list(REMOVE_ITEM ARGN OUT_DEPENDENCY _find_dependency)
    # Force CONFIG mode
    list(REMOVE_ITEM ARGN MODULE NO_CONFIG NO_MODULE)
    string(TOUPPER ${pkgname} key)
    if(DEFINED GDAL_USE_${key} AND NOT GDAL_USE_${key})
        set(${pkgname}_FOUND)
        set(${key}_FOUND)
        return()
    endif()
    find_package(${pkgname} ${ARGN}
        QUIET
        CONFIG
        GLOBAL
        # Forbid the use of system libs entirely
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
    # Add variables with upper-case package name in addition to the default ones
    set(targets "")
    foreach(lib ${${pkgname}_LIBRARIES})
        if(TARGET ${lib})
            list(APPEND targets ${lib})
        endif()
    endforeach()
    # Add upper-case variables
    set(${key}_DEFINITIONS "${${pkgname}_DEFINITIONS}" CACHE STRING "")
    set(${key}_FOUND ${${pkgname}_FOUND} CACHE BOOL "")
    set(${key}_INCLUDE_DIR "${${pkgname}_INCLUDE_DIR}" CACHE STRING "")
    set(${key}_INCLUDE_DIRS "${${pkgname}_INCLUDE_DIRS}" CACHE STRING "")
    set(${key}_LIBRARIES "${${pkgname}_LIBRARIES}" CACHE STRING "")
    set(${key}_LIBRARY "${${pkgname}_LIBRARIES}" CACHE STRING "")
    set(${key}_TARGET "${targets}" CACHE STRING "")
    set(${key}_VERSION ${${pkgname}_VERSION} CACHE BOOL "")

    # Add as cache vars for global visibility
    set(${pkgname}_FOUND ${${pkgname}_FOUND} CACHE BOOL "")
    set(${pkgname}_TARGET "${targets}" CACHE STRING "")
    set(${pkgname}_VERSION ${${pkgname}_VERSION_STRING} CACHE BOOL "")

    message(STATUS "Found ${pkgname}: ${${pkgname}_FOUND}")
    message(STATUS "  ${key}_TARGET: ${${key}_TARGET}")
    message(STATUS "  ${key}_LIBRARIES: ${${key}_LIBRARIES}")
    message(STATUS "  ${key}_INCLUDE_DIRS: ${${key}_INCLUDE_DIRS}")
endfunction()
