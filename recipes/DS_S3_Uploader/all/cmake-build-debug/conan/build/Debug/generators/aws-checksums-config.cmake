########## MACROS ###########################################################################
#############################################################################################

# Requires CMake > 3.15
if(${CMAKE_VERSION} VERSION_LESS "3.15")
    message(FATAL_ERROR "The 'CMakeDeps' generator only works with CMake >= 3.15")
endif()

if(aws-checksums_FIND_QUIETLY)
    set(aws-checksums_MESSAGE_MODE VERBOSE)
else()
    set(aws-checksums_MESSAGE_MODE STATUS)
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmakedeps_macros.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/aws-checksumsTargets.cmake)
include(CMakeFindDependencyMacro)

check_build_type_defined()

foreach(_DEPENDENCY ${aws-checksums_FIND_DEPENDENCY_NAMES} )
    # Check that we have not already called a find_package with the transitive dependency
    if(NOT ${_DEPENDENCY}_FOUND)
        find_dependency(${_DEPENDENCY} REQUIRED ${${_DEPENDENCY}_FIND_MODE})
    endif()
endforeach()

set(aws-checksums_VERSION_STRING "0.1.18")
set(aws-checksums_INCLUDE_DIRS ${aws-checksums_INCLUDE_DIRS_DEBUG} )
set(aws-checksums_INCLUDE_DIR ${aws-checksums_INCLUDE_DIRS_DEBUG} )
set(aws-checksums_LIBRARIES ${aws-checksums_LIBRARIES_DEBUG} )
set(aws-checksums_DEFINITIONS ${aws-checksums_DEFINITIONS_DEBUG} )


# Only the last installed configuration BUILD_MODULES are included to avoid the collision
foreach(_BUILD_MODULE ${aws-checksums_BUILD_MODULES_PATHS_DEBUG} )
    message(${aws-checksums_MESSAGE_MODE} "Conan: Including build module from '${_BUILD_MODULE}'")
    include(${_BUILD_MODULE})
endforeach()


