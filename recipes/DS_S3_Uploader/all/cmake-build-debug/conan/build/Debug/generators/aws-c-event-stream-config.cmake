########## MACROS ###########################################################################
#############################################################################################

# Requires CMake > 3.15
if(${CMAKE_VERSION} VERSION_LESS "3.15")
    message(FATAL_ERROR "The 'CMakeDeps' generator only works with CMake >= 3.15")
endif()

if(aws-c-event-stream_FIND_QUIETLY)
    set(aws-c-event-stream_MESSAGE_MODE VERBOSE)
else()
    set(aws-c-event-stream_MESSAGE_MODE STATUS)
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmakedeps_macros.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/aws-c-event-streamTargets.cmake)
include(CMakeFindDependencyMacro)

check_build_type_defined()

foreach(_DEPENDENCY ${aws-c-event-stream_FIND_DEPENDENCY_NAMES} )
    # Check that we have not already called a find_package with the transitive dependency
    if(NOT ${_DEPENDENCY}_FOUND)
        find_dependency(${_DEPENDENCY} REQUIRED ${${_DEPENDENCY}_FIND_MODE})
    endif()
endforeach()

set(aws-c-event-stream_VERSION_STRING "0.4.2")
set(aws-c-event-stream_INCLUDE_DIRS ${aws-c-event-stream_INCLUDE_DIRS_DEBUG} )
set(aws-c-event-stream_INCLUDE_DIR ${aws-c-event-stream_INCLUDE_DIRS_DEBUG} )
set(aws-c-event-stream_LIBRARIES ${aws-c-event-stream_LIBRARIES_DEBUG} )
set(aws-c-event-stream_DEFINITIONS ${aws-c-event-stream_DEFINITIONS_DEBUG} )


# Only the last installed configuration BUILD_MODULES are included to avoid the collision
foreach(_BUILD_MODULE ${aws-c-event-stream_BUILD_MODULES_PATHS_DEBUG} )
    message(${aws-c-event-stream_MESSAGE_MODE} "Conan: Including build module from '${_BUILD_MODULE}'")
    include(${_BUILD_MODULE})
endforeach()


