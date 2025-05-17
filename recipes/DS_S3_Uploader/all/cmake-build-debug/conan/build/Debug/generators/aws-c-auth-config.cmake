########## MACROS ###########################################################################
#############################################################################################

# Requires CMake > 3.15
if(${CMAKE_VERSION} VERSION_LESS "3.15")
    message(FATAL_ERROR "The 'CMakeDeps' generator only works with CMake >= 3.15")
endif()

if(aws-c-auth_FIND_QUIETLY)
    set(aws-c-auth_MESSAGE_MODE VERBOSE)
else()
    set(aws-c-auth_MESSAGE_MODE STATUS)
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmakedeps_macros.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/aws-c-authTargets.cmake)
include(CMakeFindDependencyMacro)

check_build_type_defined()

foreach(_DEPENDENCY ${aws-c-auth_FIND_DEPENDENCY_NAMES} )
    # Check that we have not already called a find_package with the transitive dependency
    if(NOT ${_DEPENDENCY}_FOUND)
        find_dependency(${_DEPENDENCY} REQUIRED ${${_DEPENDENCY}_FIND_MODE})
    endif()
endforeach()

set(aws-c-auth_VERSION_STRING "0.7.16")
set(aws-c-auth_INCLUDE_DIRS ${aws-c-auth_INCLUDE_DIRS_DEBUG} )
set(aws-c-auth_INCLUDE_DIR ${aws-c-auth_INCLUDE_DIRS_DEBUG} )
set(aws-c-auth_LIBRARIES ${aws-c-auth_LIBRARIES_DEBUG} )
set(aws-c-auth_DEFINITIONS ${aws-c-auth_DEFINITIONS_DEBUG} )


# Only the last installed configuration BUILD_MODULES are included to avoid the collision
foreach(_BUILD_MODULE ${aws-c-auth_BUILD_MODULES_PATHS_DEBUG} )
    message(${aws-c-auth_MESSAGE_MODE} "Conan: Including build module from '${_BUILD_MODULE}'")
    include(${_BUILD_MODULE})
endforeach()


