function(define_find_package2 pkgname include_file library_name)
endfunction()
function(find_package2 pkgname)
    # Remove args unsupported by find_package()
    list(REMOVE_ITEM ARGN OUT_DEPENDENCY _find_dependency)
    # Force CONFIG mode
    list(REMOVE_ITEM ARGN MODULE NO_CONFIG NO_MODULE)
    find_package(${pkgname} ${ARGN}
        QUIET
        CONFIG
        # Forbid the use of system libs entirely
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
    # Add variables with upper-case package name in addition to the default ones
    string(TOUPPER ${pkgname} key)
    set(targets "")
    foreach(lib ${${pkgname}_LIBRARIES})
        if(TARGET ${lib})
            list(APPEND targets ${lib})
        endif()
    endforeach()
    set(${key}_TARGET "${targets}" CACHE STRING "")
    set(${pkgname}_TARGET "${targets}" CACHE STRING "")
    set(${key}_LIBRARIES "${${pkgname}_LIBRARIES}" CACHE STRING "")
    set(${key}_LIBRARY "${${pkgname}_LIBRARIES}" CACHE STRING "")
    set(${key}_INCLUDE_DIR "${${pkgname}_INCLUDE_DIR}" CACHE STRING "")
    set(${key}_INCLUDE_DIRS "${${pkgname}_INCLUDE_DIRS}" CACHE STRING "")
    set(${key}_DEFINITIONS "${${pkgname}_DEFINITIONS}" CACHE STRING "")
    set(${key}_FOUND ${${pkgname}_FOUND} CACHE BOOL "")
    set(${pkgname}_VERSION ${${pkgname}_VERSION_STRING} CACHE BOOL "")
    set(${key}_VERSION ${${pkgname}_VERSION} CACHE BOOL "")

    message(STATUS "Found ${pkgname}: ${${pkgname}_FOUND}")
    message(STATUS "  ${key}_TARGET: ${${key}_TARGET}")
    message(STATUS "  ${key}_LIBRARIES: ${${key}_LIBRARIES}")
    message(STATUS "  ${key}_INCLUDE_DIRS: ${${key}_INCLUDE_DIRS}")
endfunction()
