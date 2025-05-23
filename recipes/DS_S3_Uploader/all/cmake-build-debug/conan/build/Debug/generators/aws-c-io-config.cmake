########## MACROS ###########################################################################
#############################################################################################

# Requires CMake > 3.15
if(${CMAKE_VERSION} VERSION_LESS "3.15")
    message(FATAL_ERROR "The 'CMakeDeps' generator only works with CMake >= 3.15")
endif()

if(aws-c-io_FIND_QUIETLY)
    set(aws-c-io_MESSAGE_MODE VERBOSE)
else()
    set(aws-c-io_MESSAGE_MODE STATUS)
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmakedeps_macros.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/aws-c-ioTargets.cmake)
include(CMakeFindDependencyMacro)

check_build_type_defined()

foreach(_DEPENDENCY ${aws-c-io_FIND_DEPENDENCY_NAMES} )
    # Check that we have not already called a find_package with the transitive dependency
    if(NOT ${_DEPENDENCY}_FOUND)
        find_dependency(${_DEPENDENCY} REQUIRED ${${_DEPENDENCY}_FIND_MODE})
    endif()
endforeach()

set(aws-c-io_VERSION_STRING "0.14.7")
set(aws-c-io_INCLUDE_DIRS ${aws-c-io_INCLUDE_DIRS_DEBUG} )
set(aws-c-io_INCLUDE_DIR ${aws-c-io_INCLUDE_DIRS_DEBUG} )
set(aws-c-io_LIBRARIES ${aws-c-io_LIBRARIES_DEBUG} )
set(aws-c-io_DEFINITIONS ${aws-c-io_DEFINITIONS_DEBUG} )


# Only the last installed configuration BUILD_MODULES are included to avoid the collision
foreach(_BUILD_MODULE ${aws-c-io_BUILD_MODULES_PATHS_DEBUG} )
    message(${aws-c-io_MESSAGE_MODE} "Conan: Including build module from '${_BUILD_MODULE}'")
    include(${_BUILD_MODULE})
endforeach()


