function(define_find_package2 pkgname include_file library_name)
endfunction()
function(find_package2 pkgname)
    find_package(${pkgname}
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
    set(${pkgname}_DEFINITIONS "${${pkgname}_DEFINITIONS}" CACHE STRING "")
    set(${pkgname}_FOUND ${${pkgname}_FOUND} CACHE BOOL "")
    set(${pkgname}_INCLUDE_DIR "${${pkgname}_INCLUDE_DIR}" CACHE STRING "")
    set(${pkgname}_INCLUDE_DIRS "${${pkgname}_INCLUDE_DIRS}" CACHE STRING "")
    set(${pkgname}_LIBRARIES "${${pkgname}_LIBRARIES}" CACHE STRING "")
    set(${pkgname}_LIBRARY "${${pkgname}_LIBRARIES}" CACHE STRING "")
    set(${pkgname}_TARGET "${targets}" CACHE STRING "")
    set(${pkgname}_VERSION ${${pkgname}_VERSION_STRING} CACHE STRING "")
endfunction()
